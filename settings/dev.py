from .base import *  # noqa

DEBUG = True

SITE_URL = 'http://127.0.0.1:8000'

ALLOWED_HOSTS = ['*']

BUNDLE_NAME = 'FAKE'  # FAKE, MTS, ITE-uat, ITE-testing, PRD

try:
    from .local import *
except ImportError:
    pass
