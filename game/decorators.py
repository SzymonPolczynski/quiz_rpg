from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def character_required(view_func):
    """
    Decorator to ensure that the user has a character created.
    Redirects to character creation if not.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not hasattr(request.user, "character") or request.user.character is None:
            messages.warning(request, "You need to create a character first.")
            return redirect("create_character")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
