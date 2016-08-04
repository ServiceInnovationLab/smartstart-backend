# global util functions, should not depend any apps.
from django.conf import settings
from django.core.urlresolvers import reverse


def full_reverse(*args, site_url=None, **kwargs):
    """Reverse to a full url"""
    return (site_url or settings.SITE_URL).rstrip('/') + reverse(*args, **kwargs)


def get_text_body(key, begin='', end=''):
    """Get body part by removing begin and end from text"""
    return key.strip().strip(begin).strip(end).strip()


def get_cer_body(key):
    begin = '-----BEGIN CERTIFICATE-----'
    end = '-----END CERTIFICATE-----'
    return get_text_body(key, begin=begin, end=end)


def get_private_key_body(key):
    begin = '-----BEGIN PRIVATE KEY-----'
    end = '-----END PRIVATE KEY-----'
    return get_text_body(key, begin=begin, end=end)
