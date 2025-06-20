from django.conf import settings
from .models import ContactInfo


def global_settings(request):
    return {
        'debug': settings.DEBUG,
    }

def contact_info(request):
    try:
        info = ContactInfo.objects.first()
    except ContactInfo.DoesNotExist:
        info = None
    return {'contact_info': info}