from django.conf import settings

def wordpress(request):
    try:
        return { 'WORDPRESS': settings.WORDPRESS }
    except AttributeError:
        return { 'WORDPRESS': None }

