import random
from django.shortcuts import render, redirect
from .models import Character, Question, Answer
from django.contrib.auth.decorators import login_required
from .forms import CharasterClassForm


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
                gained_xp = character.get_xp_reward()
                feedback = f"Correct! +{gained_xp} experience points awarded. <br>"
                character.experience += gained_xp
                if character.experience >= character.level * 100:
                    character.level += 1
                    character.experience = 0
                    feedback += f" Level up! You are now level {character.level}."
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
