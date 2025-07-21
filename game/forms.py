from django import forms
from .models import Character


class CharasterClassForm(forms.ModelForm):
    """Form for selecting character class."""

    class Meta:
        model = Character
        fields = ["character_class"]
        widgets = {"character_class": forms.RadioSelect}
