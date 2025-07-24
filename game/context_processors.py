from .models import Character


def character_context(request):
    if request.user.is_authenticated:
        try:
            character = Character.objects.get(user=request.user)
            return {"character": character}
        except Character.DoesNotExist:
            return {}
    return {}
