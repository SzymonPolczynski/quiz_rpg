import random


def player_attack(character, enemy, enemy_hp):
    dmg = random.randint(character.physical_min_damage, character.physical_max_damage)
    dmg_after_armor = max(dmg - enemy.armor, 0)
    enemy_hp -= dmg_after_armor
    return max(enemy_hp, 0), dmg_after_armor


def enemy_attack(enemy, character):
    dmg = max(enemy.power - character.armor, 0)
    character.hp = max(character.hp - dmg, 0)
    return character.hp, dmg


def resolve_battle_turn(character, enemy, enemy_hp):
    logs = []
    enemy_hp, player_dmg = player_attack(character, enemy, enemy_hp)
    logs.append(f"You hit {enemy.name} for {player_dmg} dmg!")

    if enemy_hp <= 0:
        return {
            "enemy_defeated": True,
            "character_defeated": False,
            "enemy_hp": 0,
            "logs": logs,
            "enemy_dmg": 0,
        }
    
    character.hp, enemy_dmg = enemy_attack(enemy, character)
    logs.append(f"{enemy.name} hit you for {enemy_dmg} dmg!")

    return {
        "enemy_defeated": False,
        "character_defeated": character.hp <= 0,
        "enemy_hp": enemy_hp,
        "logs": logs,
        "enemy_dmg": enemy_dmg,
    }
