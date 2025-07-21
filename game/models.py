from django.db import models
from django.contrib.auth.models import User


class Character(models.Model):
    """Model representing a game character."""
    
    CLASS_CHOICES = [
        ("warrior", "Warrior"),
        ("mage", "Mage"),
        ("rogue", "Rogue"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    character_class = models.CharField(max_length=20, choices=CLASS_CHOICES, default="warrior")
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Level {self.level}, Class: {self.character_class})"


class Question(models.Model):
    """Model representing a quiz question."""

    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Answer(models.Model):
    """Model representing an answer to a quiz question."""

    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'✔' if self.is_correct else '✖'})"
