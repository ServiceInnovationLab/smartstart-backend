from .base import *  # noqa

DEBUG = True

# USER = os.environ['USER']
# SITE_DOMAIN = '{}.dev.boac.lef'.format(USER)
SITE_URL = 'http://127.0.0.1:8000'

ALLOWED_HOSTS = ['*']

IDP = 'FAKE'  # FAKE, MTS, ITS, PRD

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
