import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Character, Question, Answer, Item, Category, Quest, QuestProgress, Enemy
from django.contrib.auth.decorators import login_required
from .decorators import character_required
from .forms import CharasterClassForm, StatAllocationForm
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from game.services.leveling import check_level_up
from game.services.stats import recalculate_character_stats
from game.services.regeneration import regenerate_character


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("create_character")
    else:
        form = UserCreationForm()
    return render(request, "game/register.html", {"form": form})


@character_required
def home_view(request):
    character = request.user.character
    regenerate_character(character)
    return render(request, "game/home.html")


@login_required
def choose_class_view(request):
    character = Character.objects.get(user=request.user)

    if request.method == "POST":
        form = CharasterClassForm(request.POST, instance=character)
        if form.is_valid():
            form.save()
            return redirect("quiz")
    else:
        form = CharasterClassForm(instance=character)

    return render(request, "game/choose_class.html", {"form": form})


@character_required
def quiz_view(request):
    character, created = Character.objects.get_or_create(
        user=request.user,
        defaults={"name": request.user.username},
    )

    regenerate_character(character)

    category_id = request.session.get("selected_category")
    questions = Question.objects.all()

    if category_id:
        questions = questions.filter(category_id=category_id)

    if not questions.exists():
        return render(request, "game/no_questions.html", {"category_id": category_id})

    if not character.character_class:
        return redirect("choose_class")

    feedback = request.session.pop("feedback", None)
    question = random.choice(questions)

    if request.method == "POST":
        selected_answer_id = request.POST.get("answer")
        if selected_answer_id:
            answer = Answer.objects.get(id=selected_answer_id)

            # Calculate XP reward based on the character's stats
            if answer.is_correct:
                reward = character.get_xp_reward()
                feedback = f"Correct! <br>"
                feedback += f"Strength Bonus: {reward['strength_bonus']} <br>"
                feedback += f"Intelligence Bonus: {reward['intelligence_bonus']} <br>"
                if reward["double"]:
                    feedback += "Lucky! You received double XP! <br>"
                feedback += f"Total XP: {reward['total']} <br>"
                feedback += f"Gold earned: 2 <br>"
                character.gold += 2
                character.experience += reward["total"]
                check_level_up(character)

                # Quest progression
                active_quests = QuestProgress.objects.filter(
                    character=character, is_completed=False
                )
                for progress in active_quests:
                    if progress.quest.category == question.category:
                        progress.correct_answers += 1
                        if (
                            progress.correct_answers
                            >= progress.quest.required_correct_answers
                        ):
                            progress.is_completed = True
                        messages.success(
                            request, f"Quest completed: {progress.quest.name}!"
                        )
                        progress.save()
                character.save()
            else:
                feedback = "Wrong answer."
        request.session["feedback"] = feedback
        return redirect("quiz")

    return render(
        request,
        "game/quiz.html",
        {"question": question, "character": character, "feedback": feedback},
    )


@character_required
def profile_view(request):
    SLOTS = [
        ("head", "Head"),
        ("body", "Body"),
        ("legs", "Legs"),
        ("feet", "Feet"),
        ("hand_right", "Right Hand"),
        ("hand_left", "Left Hand"),
    ]

    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    xp_max = character.level * 100
    xp_progress = int((character.experience / xp_max) * 100)
    equipped_items = []
    for slot, label in SLOTS:
        item = getattr(character, f"equipped_{slot}")
        equipped_items.append(
            {
                "slot": slot,
                "label": label,
                "item": item,
            }
        )

    return render(
        request,
        "game/profile.html",
        {
            "character": character,
            "xp_progress": xp_progress,
            "equipped_items": equipped_items,
        },
    )


@character_required
def allocate_stats_view(request):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)

    if request.method == "POST":
        form = StatAllocationForm(request.POST)
        if form.is_valid():
            new_values = form.cleaned_data

            before = {
                "strength": character.strength,
                "intelligence": character.intelligence,
                "dexterity": character.dexterity,
                "vitality": character.vitality,
                "luck": character.luck,
            }

            total_used = sum(max(0, new_values[k] - before[k]) for k in before)

            if total_used > character.stat_points:
                form.add_error(None, "You do not have enough stat points.")
            else:
                character.strength = new_values["strength"]
                character.intelligence = new_values["intelligence"]
                character.dexterity = new_values["dexterity"]
                character.vitality = new_values["vitality"]
                character.luck = new_values["luck"]
                character.stat_points -= total_used
                recalculate_character_stats(character)
                character.save()
                return redirect("profile")
    else:
        form = StatAllocationForm(
            initial={
                "strength": character.strength,
                "intelligence": character.intelligence,
                "dexterity": character.dexterity,
                "vitality": character.vitality,
                "luck": character.luck,
            }
        )

    return render(
        request,
        "game/allocate_stats.html",
        {
            "form": form,
            "character": character,
        },
    )


@character_required
def inventory_view(request):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    items = character.items.all()

    return render(
        request,
        "game/inventory.html",
        {
            "items": items,
            "character": character,
        },
    )


@login_required
def use_item_view(request, item_id):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    item = Item.objects.get(id=item_id)

    character.strength += item.effect_strength
    character.intelligence += item.effect_intelligence
    character.dexterity += item.effect_dexterity
    character.luck += item.effect_luck

    character.items.remove(item)
    character.save()

    return redirect("inventory")


@login_required
def equip_item_view(request, item_id):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    item = Item.objects.get(id=item_id)

    # Check if the item can be equipped
    slot = item.slot
    current_equipped = getattr(character, f"equipped_{slot}")

    # If there's already an item equipped in that slot, add it back to the inventory
    # before equipping the new item
    if current_equipped:
        character.items.add(current_equipped)

    setattr(character, f"equipped_{slot}", item)
    character.items.remove(item)
    recalculate_character_stats(character)
    character.save()

    return redirect("profile")


@login_required
def unequip_item_view(request, slot):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)

    try:
        equipeed_item = getattr(character, f"equipped_{slot}")
        if equipeed_item:
            character.items.add(equipeed_item)
            setattr(character, f"equipped_{slot}", None)
            recalculate_character_stats(character)
            character.save()
    except AttributeError:
        pass  # Handle case where slot does not exist

    return redirect("profile")


@login_required
def choose_category_view(request):
    categories = Category.objects.all()
    return render(request, "game/choose_category.html", {"categories": categories})


@login_required
def set_category_view(request, category_id):
    request.session["selected_category"] = category_id
    return redirect("quiz")


@login_required
def clear_category_view(request):
    request.session.pop("selected_category", None)
    return redirect("choose_category")


@character_required
def shop_view(request):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    items = Item.objects.filter(is_available_in_shop=True)

    return render(
        request,
        "game/shop.html",
        {
            "items": items,
            "character": character,
        },
    )


@login_required
def buy_item_view(request, item_id):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    item = get_object_or_404(Item, id=item_id)

    if item.price and character.gold >= item.price:
        character.gold -= item.price
        character.items.add(item)
        character.save()
        messages.success(request, f"You bought {item.name} for {item.price} gold.")
    else:
        messages.warning(request, "You do not have enough gold to buy this item.")

    return redirect("shop")


@login_required
def sell_item_view(request, item_id):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    item = get_object_or_404(Item, id=item_id)

    if item in character.items.all():
        sell_price = item.price // 2 if item.price else 0
        character.gold += sell_price
        character.items.remove(item)
        character.save()
        messages.success(request, f"You sold {item.name} for {sell_price} gold.")
    else:
        messages.warning(request, "You do not own this item.")

    return redirect("inventory")


@character_required
def quest_list_view(request):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    accepted_ids = QuestProgress.objects.filter(character=character).values_list(
        "quest_id", flat=True
    )
    available_quests = Quest.objects.exclude(id__in=accepted_ids)

    return render(request, "game/quest_list.html", {"quests": available_quests})


@login_required
def accept_quest_view(request, quest_id):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    quest = get_object_or_404(Quest, id=quest_id)

    QuestProgress.objects.get_or_create(character=character, quest=quest)

    messages.success(request, f"You have accepted the quest: {quest.name}.")

    return redirect("quest_list")


@character_required
def quest_log_view(request):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    active_quests = QuestProgress.objects.filter(
        character=character, is_completed=False
    )
    ready_to_claim = QuestProgress.objects.filter(
        character=character, is_completed=True, reward_claimed=False
    )
    claimed = QuestProgress.objects.filter(
        character=character, is_completed=True, reward_claimed=True
    )

    return render(
        request,
        "game/quest_log.html",
        {
            "active_quests": active_quests,
            "ready_to_claim": ready_to_claim,
            "claimed": claimed,
        },
    )


@login_required
def claim_quest_reward_view(request, progress_id):
    character = Character.objects.get(user=request.user)
    regenerate_character(character)
    progress = get_object_or_404(QuestProgress, id=progress_id, character=character)

    if progress.is_completed and not progress.reward_claimed:
        character.experience += progress.quest.experience_reward
        character.gold += progress.quest.gold_reward

        if progress.quest.item_reward:
            character.items.add(progress.quest.item_reward)
            item_info = f" and received item: {progress.quest.item_reward.name}"
        else:
            item_info = ""

        progress.reward_claimed = True
        progress.date_completed = timezone.now()
        progress.save()
        character.save()

        check_level_up(character)

        messages.success(
            request,
            f"Reward claimed: +{progress.quest.experience_reward} XP, +{progress.quest.gold_reward} gold{item_info}.",
        )
    else:
        messages.warning(request, "You cannot claim this reward.")

    return redirect("quest_log")


@login_required
def create_character_view(request):
    if hasattr(request.user, "character"):
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")
        class_choice = request.POST.get("class")

        if name and class_choice:
            character = Character.objects.create(
                user=request.user,
                name=name,
                character_class=class_choice,
            )
            recalculate_character_stats(character)
            character.save()
            return redirect("home")

    return render(request, "game/create_character.html")


@character_required
def battle_view(request):
    character = request.user.character
    regenerate_character(character)

    enemy_id = request.session.get("current_enemy_id")

    if enemy_id:
        enemy = Enemy.objects.filter(id=enemy_id).first()

        if not enemy:
            enemy = random.choice(Enemy.objects.all())
            request.session["current_enemy_id"] = enemy.pk
            request.session["enemy_hp"] = enemy.max_hp

    else:
        enemy = random.choice(Enemy.objects.all())
        request.session["current_enemy_id"] = enemy.pk
        request.session["enemy_hp"] = enemy.max_hp

    enemy_hp = request.session.get("enemy_hp", enemy.max_hp)

    if request.method == "POST":
        dmg = random.randint(character.physical_min_damage, character.physical_max_damage)
        dmg_after_armor = max(dmg - enemy.armor, 0)
        enemy_hp -= dmg_after_armor

        request.session["enemy_hp"] = enemy_hp

        if enemy_hp <= 0:
            character.experience += enemy.xp_reward
            character.gold += enemy.gold_reward
            request.session.pop("current_enemy_id", None)
            request.session.pop("enemy_hp", None)

            messages.success(request, f"You defeated {enemy.name} and earned {enemy.gold_reward} gold and {enemy.xp_reward} XP!")
            check_level_up(character)
            character.save()

            return redirect("battle")
        
        enemy_dmg = max(enemy.power - character.armor, 0)
        character.hp = max(character.hp - enemy_dmg, 0)

        if character.hp <= 0:
            request.session.pop("current_enemy_id", None)
            request.session.pop("enemy_hp", None)

            messages.error(request, f"You were defeated by {enemy.name}!")
            character.save()
            return redirect("battle_defeat")

        character.save()

        messages.info(request, f"You hit {enemy.name} for {dmg_after_armor} dmg. Enemy hit you for {enemy_dmg} dmg.")

    return render(request, "game/battle.html", {
        "enemy": enemy,
        "enemy_hp": enemy_hp,
        "character": character,
    })


@character_required
def battle_defeat_view(request):
    return render(request, "game/battle_defeat.html")


@character_required
def tavern_view(request):
    character = request.user.character
    regenerate_character(character)

    if request.method == "POST":
        if character.gold >= 20:
            character.gold -= 20
            character.hp = character.max_hp
            character.mana = character.max_mana
            character.stamina = character.max_stamina
            character.save()
            messages.success(request, "You feel rested and fully recovered!")
        else:
            messages.error(request, "Not enought gold to rest!")

        return redirect("tavern")
    
    return render(request, "game/tavern.html", {"character": character})
