from urllib.parse import urljoin
from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

register = template.Library()


@register.filter
@stringfilter
def full_url_filter(url):
    return urljoin(settings.SITE_URL, url)


@register.simple_tag
def full_url_tag(url):
    return urljoin(settings.SITE_URL, url)
