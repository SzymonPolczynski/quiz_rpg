import random
from django.db import models
from django.contrib.auth.models import User
from typing import TypedDict


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
        max_length=20, choices=CLASS_CHOICES, default="warrior")
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    items = models.ManyToManyField("Item", related_name="characters", blank=True)

    strength = models.IntegerField(default=5)
    intelligence = models.IntegerField(default=5)
    agility = models.IntegerField(default=5)
    luck = models.IntegerField(default=5)

    stat_points = models.IntegerField(default=0)
    
    class XpReward(TypedDict):
        total: int
        base: int
        strength_bonus: int
        intelligence_bonus: int
        double: bool


    def get_xp_reward(self) -> XpReward:
        base_xp = {
            "warrior": 10,
            "mage": 15,
            "rogue": 12
        }.get(self.character_class, 10)

        strength_bonus = int(base_xp * (self.strength / 100))

        intelligence_bonus = int(self.intelligence * 1)

        luck_chance = self.luck * 5
        double_reward = random.randint(1, 100) <= luck_chance

        total = base_xp + strength_bonus + intelligence_bonus
        if double_reward:
            total *= 2

        return {
            "total": total,
            "base": base_xp,
            "strength_bonus": strength_bonus,
            "intelligence_bonus": intelligence_bonus,
            "double": double_reward,
        }

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


class Item(models.Model):
    """Model representing an item in the game."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    effect_strength = models.IntegerField(default=0)
    effect_intelligence = models.IntegerField(default=0)
    effect_agility = models.IntegerField(default=0)
    effect_luck = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    