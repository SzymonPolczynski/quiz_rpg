from django import forms
from .models import Character


class CharasterClassForm(forms.ModelForm):
    """Form for selecting character class."""

    class Meta:
        model = Character
        fields = ["character_class"]
        widgets = {"character_class": forms.RadioSelect}


class StatAllocationForm(forms.Form):
    """Form for allocating stat points."""

    strength = forms.IntegerField(min_value=0)
    intelligence = forms.IntegerField(min_value=0)
    dexterity = forms.IntegerField(min_value=0)
    vitality = forms.IntegerField(min_value=0)
    luck = forms.IntegerField(min_value=0)
