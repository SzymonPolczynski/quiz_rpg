from django import template


register = template.Library()


@register.filter
def get_slot(character, slot_name):
    return getattr(character, f"equipped_{slot_name}", None)