import random
from .stats import recalculate_character_stats


def experience_to_next_level(level):
    return 100 + level * 50


def check_level_up(character):
    leveled_up = False
    while character.experience >= character.experience_to_next_level:
        character.experience -= character.experience_to_next_level
        level_up(character)
        character.experience_to_next_level = experience_to_next_level(character.level)
        leveled_up = True

    if leveled_up:
        recalculate_character_stats(character)
        character.save()


def level_up(character):
    character.level += 1
    character.stat_points += 5

    if character.character_class == "warrior":
        character.hp_from_levels += random.randint(1, 6) + random.randint(1, 6)  # 2k6
    elif character.character_class == "mage":
        character.hp_from_levels += random.randint(1, 3) + random.randint(1, 3)  # 2k3
        character.mana_from_levels += 10
    elif character.character_class == "rogue":
        character.hp_from_levels += random.randint(1, 10)  # 1k10

    recalculate_character_stats(character)
    character.save()
    