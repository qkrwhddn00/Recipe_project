# blog/context_processors.py
from django.conf import settings

def global_settings(request):
    return {
        "GLOBAL_NICKNAME": settings.GLOBAL_NICKNAME
    }