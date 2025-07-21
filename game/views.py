import random
from django.shortcuts import render, redirect
from .models import Character, Question, Answer
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):
    return render(request, "game/home.html")


@login_required
def quiz_view(request):
    character, created = Character.objects.get_or_create(
        user=request.user,
        defaults={"name": request.user.username,
                  "character_class": "warrior",}
    )

    feedback = request.session.pop("feedback", None)
    question = random.choice(Question.objects.all())

    if request.method == "POST":
        selected_answer_id = request.POST.get("answer")
        if selected_answer_id:
            answer = Answer.objects.get(id=selected_answer_id)
            if answer.is_correct:
                feedback = "Correct! +10 experience points awarded. <br>"
                character.experience += 10
                if character.experience >= character.level * 100:
                    character.level += 1
                    character.experience = 0
                    feedback += f" Level up! You are now level {character.level}."
                character.save()
            else:
                feedback = "Wrong answer."
        request.session["feedback"] = feedback        
        return redirect("quiz")

    return render(request, "game/quiz.html", {"question": question, "character": character, "feedback": feedback})
