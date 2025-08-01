import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
        max_length=20, choices=CLASS_CHOICES, default="warrior"
    )

    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    experience_to_next_level = models.PositiveIntegerField(default=100)

    hp = models.PositiveIntegerField(default=100)
    max_hp = models.PositiveIntegerField(default=100)
    hp_from_levels = models.PositiveIntegerField(default=0)

    mana = models.PositiveIntegerField(default=50)
    max_mana = models.PositiveIntegerField(default=50)
    mana_from_levels = models.PositiveIntegerField(default=0)

    stamina = models.PositiveIntegerField(default=50)
    max_stamina = models.PositiveIntegerField(default=50)

    armor = models.PositiveIntegerField(default=0)
    damage_reduction = models.FloatField(default=0.0)

    physical_min_damage = models.PositiveIntegerField(default=1)
    physical_max_damage = models.PositiveIntegerField(default=3)

    spell_power = models.PositiveIntegerField(default=0)

    hp_regeneration = models.PositiveIntegerField(default=0)
    mana_regeneration = models.PositiveIntegerField(default=0)
    stamina_regeneration = models.PositiveIntegerField(default=0)

    items = models.ManyToManyField("Item", related_name="characters", blank=True)

    equipped_head = models.ForeignKey(
        "Item",
        null=True,
        blank=True,
        related_name="equipped_on_head",
        on_delete=models.SET_NULL,
    )
    equipped_body = models.ForeignKey(
        "Item",
        null=True,
        blank=True,
        related_name="equipped_on_body",
        on_delete=models.SET_NULL,
    )
    equipped_legs = models.ForeignKey(
        "Item",
        null=True,
        blank=True,
        related_name="equipped_on_legs",
        on_delete=models.SET_NULL,
    )
    equipped_feet = models.ForeignKey(
        "Item",
        null=True,
        blank=True,
        related_name="equipped_on_feet",
        on_delete=models.SET_NULL,
    )
    equipped_hand_right = models.ForeignKey(
        "Item",
        null=True,
        blank=True,
        related_name="equipped_on_hand_right",
        on_delete=models.SET_NULL,
    )
    equipped_hand_left = models.ForeignKey(
        "Item",
        null=True,
        blank=True,
        related_name="equipped_on_hand_left",
        on_delete=models.SET_NULL,
    )

    strength = models.IntegerField(default=5)
    intelligence = models.IntegerField(default=5)
    dexterity = models.IntegerField(default=5)
    vitality = models.IntegerField(default=5)
    luck = models.IntegerField(default=5)

    stat_points = models.IntegerField(default=0)

    gold = models.IntegerField(default=0)

    last_regen_time = models.DateTimeField(default=timezone.now)

    class XpReward(TypedDict):
        total: int
        base: int
        strength_bonus: int
        intelligence_bonus: int
        double: bool

    def get_xp_reward(self) -> XpReward:
        base_xp = {"warrior": 10, "mage": 15, "rogue": 12}.get(self.character_class, 10)

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

    @property
    def total_strength(self):
        return self.strength + sum(
            item.effect_strength for item in self.get_eqquipped_items()
        )

    @property
    def total_intelligence(self):
        return self.intelligence + sum(
            item.effect_intelligence for item in self.get_eqquipped_items()
        )

    @property
    def total_dexterity(self):
        return self.dexterity + sum(
            item.effect_dexterity for item in self.get_eqquipped_items()
        )

    @property
    def total_vitality(self):
        return self.vitality + sum(
            item.effect_vitality for item in self.get_eqquipped_items()
        )

    @property
    def total_luck(self):
        return self.luck + sum(item.effect_luck for item in self.get_eqquipped_items())

    def get_eqquipped_items(self):
        return filter(
            None,
            [
                self.equipped_head,
                self.equipped_body,
                self.equipped_legs,
                self.equipped_feet,
                self.equipped_hand_right,
                self.equipped_hand_left,
            ],
        )

    def __str__(self):
        return f"{self.name} (Level {self.level}, Class: {self.character_class})"


class Question(models.Model):
    """Model representing a quiz question."""

    text = models.CharField(max_length=255)
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.text


class Answer(models.Model):
    """Model representing an answer to a quiz question."""

    question = models.ForeignKey(
        "Question", related_name="answers", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'✔' if self.is_correct else '✖'})"


class Item(models.Model):
    """Model representing an item in the game."""

    SLOT_CHOICES = [
        ("head", "Head"),
        ("body", "Body"),
        ("legs", "Legs"),
        ("feet", "Feet"),
        ("hand_right", "Right Hand"),
        ("hand_left", "Left Hand"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField(null=True, blank=True)
    is_available_in_shop = models.BooleanField(default=False)
    slot = models.CharField(
        max_length=20,
        choices=SLOT_CHOICES,
        default="hand_right",
    )

    effect_strength = models.IntegerField(default=0)
    effect_intelligence = models.IntegerField(default=0)
    effect_dexterity = models.IntegerField(default=0)
    effect_vitality = models.IntegerField(default=0)
    effect_luck = models.IntegerField(default=0)

    min_damage = models.PositiveIntegerField(default=0)
    max_damage = models.PositiveIntegerField(default=0)
    armor = models.PositiveIntegerField(default=0)
    spell_power = models.PositiveIntegerField(default=0)

    hp_bonus = models.IntegerField(default=0)
    mana_bonus = models.IntegerField(default=0)
    stamina_bonus = models.IntegerField(default=0)

    required_class = models.CharField(
        max_length=20,
        choices=Character.CLASS_CHOICES,
        null=True,
        blank=True,
        help_text="If set, only characters of this class can equip the item.",
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    """Model representing a category for quiz questions."""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Quest(models.Model):
    """Model representing a quest in the game."""

    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    required_correct_answers = models.PositiveIntegerField(default=1)
    experience_reward = models.PositiveIntegerField(default=0)
    gold_reward = models.PositiveIntegerField(default=0)
    item_reward = models.ForeignKey(
        "Item", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name


class QuestProgress(models.Model):
    """Model representing the progress of a quest for a character."""

    character = models.ForeignKey("Character", on_delete=models.CASCADE)
    quest = models.ForeignKey("Quest", on_delete=models.CASCADE)
    correct_answers = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    reward_claimed = models.BooleanField(default=False)

    date_started = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    def complete(self):
        self.is_completed = True
        self.date_completed = timezone.now()
        self.save()

    def is_ready_to_claim(self):
        return self.is_completed and not self.reward_claimed

    def __str__(self):
        return f"{self.character.user.username} - {self.quest.name} ({'Completed' if self.is_completed else 'In Progress'})"


class Enemy(models.Model):
    """Model representing the enemy in PvE encounters."""

    DIFFICULTY_CHOICES = [
    ("easy", "Easy"),
    ("medium", "Medium"),
    ("hard", "Hard"),
    ("boss", "Boss"),
    ]

    name = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="easy")
    max_hp = models.PositiveIntegerField(default=100)
    power = models.PositiveIntegerField(default=10)
    armor = models.PositiveIntegerField(default=0)
    gold_reward = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
