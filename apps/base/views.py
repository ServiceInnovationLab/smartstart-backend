from django.conf import settings
from django.http import HttpResponse
from .models import SiteLocker


def make_live_view(request, site_hash):
    """
    Pretend this URL doesn't exist (404) unless the hash matches.
    If so, make this instance "live".
    """
    if site_hash == settings.SITE_HASH:
        locker = SiteLocker()
        locker.make_live()
        return HttpResponse(status=200, content='OK')
    return HttpResponse(status=404)
