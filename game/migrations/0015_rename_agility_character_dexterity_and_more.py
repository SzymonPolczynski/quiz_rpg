# Generated by Django 5.2.4 on 2025-07-25 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0014_item_armor_item_hp_bonus_item_mana_bonus_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="character",
            old_name="agility",
            new_name="dexterity",
        ),
        migrations.RenameField(
            model_name="item",
            old_name="effect_agility",
            new_name="effect_dexterity",
        ),
    ]
