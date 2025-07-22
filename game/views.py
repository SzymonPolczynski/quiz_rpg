import random
from django.shortcuts import render, redirect
from .models import Character, Question, Answer, Item
from django.contrib.auth.decorators import login_required
from .forms import CharasterClassForm, StatAllocationForm


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

    if not character.character_class:
        return redirect("choose_class")

    feedback = request.session.pop("feedback", None)
    question = random.choice(Question.objects.all())

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
    character = Character.objects.get(user=request.user)
    xp_max = character.level * 100
    xp_progress = int((character.experience / xp_max) * 100)
    return render(
        request,
        "game/profile.html",
        {"character": character, "xp_progress": xp_progress},
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

            total_used = sum(
                max(0, new_values[k] - before[k]) for k in before
            )

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
        form = StatAllocationForm(initial={
            "strength": character.strength,
            "intelligence": character.intelligence,
            "agility": character.agility,
            "luck": character.luck,
        })
    
    return render(request, "game/allocate_stats.html", {
        "form": form,
        "character": character,
    })


@login_required
def inventory_view(request):
    character = Character.objects.get(user=request.user)
    items = character.items.all()
    
    return render(request, "game/inventory.html", {
        "items": items,
        "character": character,        
    })


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
