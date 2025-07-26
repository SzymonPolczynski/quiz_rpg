def calculate_max_hp(vitality, hp_from_levels):
    return hp_from_levels + vitality * 10


def calculate_max_mana(intelligence, mana_from_levels):
    return mana_from_levels + intelligence * 8


def calculate_max_stamina(dexterity, vitality):
    return 50 + dexterity * 4 + vitality * 2


def calculate_physical_damage(strength, min_weapon_dmg, max_weapon_dmg):
    bonus = int(strength * 0.5)
    return (min_weapon_dmg + bonus, max_weapon_dmg + bonus)


def calculate_spell_power(intelligence, item_bonus):
    return intelligence * 2 + item_bonus


def recalculate_character_stats(character):
    equipment = [
        character.equipped_head,
        character.equipped_body,
        character.equipped_legs,
        character.equipped_feet,
        character.equipped_hand_right,
        character.equipped_hand_left,
    ]

    total_hp_bonus = total_mana_bonus = total_stamina_bonus = 0
    total_armor = total_spell_power = 0
    weapon_min_dmg = weapon_max_dmg = 0

    for item in equipment:
        if item:
            total_hp_bonus += item.hp_bonus
            total_mana_bonus += item.mana_bonus
            total_stamina_bonus += item.stamina_bonus
            total_armor += item.armor
            total_spell_power += item.spell_power

            if item.min_damage or item.max_damage:
                weapon_min_dmg = item.min_damage
                weapon_max_dmg = item.max_damage

    character.max_hp = (
        calculate_max_hp(character.vitality, character.hp_from_levels) + total_hp_bonus
    )
    character.max_mana = (
        calculate_max_mana(character.intelligence, character.mana_from_levels)
        + total_mana_bonus
    )
    character.max_stamina = (
        calculate_max_stamina(character.dexterity, character.vitality)
        + total_stamina_bonus
    )

    character.hp = min(character.hp, character.max_hp)
    character.mana = min(character.mana, character.max_mana)
    character.stamina = min(character.stamina, character.max_stamina)

    character.armor = total_armor
    character.damage_reduction = round(min(total_armor / (total_armor + 100), 0.75), 3)
    character.spell_power = calculate_spell_power(
        character.intelligence, total_spell_power
    )
    character.physical_min_damage, character.physical_max_damage = (
        calculate_physical_damage(character.strength, weapon_min_dmg, weapon_max_dmg)
    )

    character.save()
