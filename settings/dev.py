from .base import *  # noqa

DEBUG = True

SITE_URL = 'http://127.0.0.1:8000'

ALLOWED_HOSTS = ['*']

IDP = 'FAKE'  # FAKE, MTS, ITE-uat, ITE-testing, PRD

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


try:
    from .local import *
except ImportError:
    pass
