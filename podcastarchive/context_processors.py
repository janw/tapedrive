from django.conf import settings


def debug(request):
    """
    Return additional context variables helpful for debugging parts of the project.
    """
    context_extras = {}
    if request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS:
        context_extras["DEBUG_FRONTEND"] = getattr(settings, "DEBUG_FRONTEND", False)
    return context_extras
