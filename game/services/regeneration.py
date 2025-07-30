from django.utils import timezone
from datetime import timedelta


REGEN_INTERVAL = timedelta(minutes=1)
REGEN_AMOUNT = 1


def regenerate_character(character):
    now = timezone.now()
    elapsed = now - character.last_regen_time
    ticks = elapsed // REGEN_INTERVAL

    if ticks >= 1:
        character.hp = min(character.max_hp, character.hp + ticks * REGEN_AMOUNT)
        character.mana = min(character.max_mana, character.mana + ticks * REGEN_AMOUNT)
        character.stamina = min(
            character.max_stamina, character.stamina + ticks * REGEN_AMOUNT
        )
        character.last_regen_time = now
        character.save()
