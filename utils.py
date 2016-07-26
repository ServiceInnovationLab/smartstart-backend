# global util functions, should not depend any apps.
from django.conf import settings
from django.core.urlresolvers import reverse


def full_reverse(*args, **kwargs):
    """Reverse to a full url"""
    return settings.SITE_URL.rstrip('/') + reverse(*args, **kwargs)
