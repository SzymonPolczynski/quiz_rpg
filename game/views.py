import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Character, Question, Answer, Item, Category
from django.contrib.auth.decorators import login_required
from .forms import CharasterClassForm, StatAllocationForm
from django.contrib import messages


@login_required
def home_view(request):
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


@login_required
def quiz_view(request):
    character, created = Character.objects.get_or_create(
        user=request.user,
        defaults={"name": request.user.username},
    )

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
                if character.experience >= character.level * 100:
                    character.level += 1
                    character.experience = 0
                    character.stat_points += 5
                    feedback += f" Level up! You are now level {character.level}. <br>"
                    feedback += f" You have {character.stat_points} stat points to distribute. <br>"
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


@login_required
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


@login_required
def allocate_stats_view(request):
    character = Character.objects.get(user=request.user)

    if request.method == "POST":
        form = StatAllocationForm(request.POST)
        if form.is_valid():
            new_values = form.cleaned_data

            before = {
                "strength": character.strength,
                "intelligence": character.intelligence,
                "agility": character.agility,
                "luck": character.luck,
            }

            total_used = sum(max(0, new_values[k] - before[k]) for k in before)

            if total_used > character.stat_points:
                form.add_error(None, "You do not have enough stat points.")
            else:
                character.strength = new_values["strength"]
                character.intelligence = new_values["intelligence"]
                character.agility = new_values["agility"]
                character.luck = new_values["luck"]
                character.stat_points -= total_used
                character.save()
                return redirect("profile")
    else:
        form = StatAllocationForm(
            initial={
                "strength": character.strength,
                "intelligence": character.intelligence,
                "agility": character.agility,
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


@login_required
def inventory_view(request):
    character = Character.objects.get(user=request.user)
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
    item = Item.objects.get(id=item_id)

    character.strength += item.effect_strength
    character.intelligence += item.effect_intelligence
    character.agility += item.effect_agility
    character.luck += item.effect_luck

    character.items.remove(item)
    character.save()

    return redirect("inventory")


@login_required
def equip_item_view(request, item_id):
    character = Character.objects.get(user=request.user)
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
    character.save()

    return redirect("profile")


@login_required
def unequip_item_view(request, slot):
    character = Character.objects.get(user=request.user)

    try:
        equipeed_item = getattr(character, f"equipped_{slot}")
        if equipeed_item:
            character.items.add(equipeed_item)
            setattr(character, f"equipped_{slot}", None)
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


@login_required
def shop_view(request):
    character = Character.objects.get(user=request.user)
    items = Item.objects.filter(is_available_in_shop=True)

    return render(request, "game/shop.html", {
        "items": items,
        "character": character,
    })


@login_required
def buy_item_view(request, item_id):
    character = Character.objects.get(user=request.user)
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
