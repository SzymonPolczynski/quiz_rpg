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
    character_class = models.CharField(
        max_length=20, choices=CLASS_CHOICES, blank=True, null=True
    )
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)

    strength = models.IntegerField(default=5)
    intelligence = models.IntegerField(default=5)
    agility = models.IntegerField(default=5)
    luck = models.IntegerField(default=5)

    def get_xp_reward(self) -> int:
        if self.character_class == "warrior":
            return 10
        elif self.character_class == "mage":
            return 15
        elif self.character_class == "rogue":
            return 12
        return 10

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
