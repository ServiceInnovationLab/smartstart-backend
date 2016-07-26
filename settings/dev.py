from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['*']

AUTH_METHOD = 'sp'  # fake, sp
SP_STAGE = 'mts'  # mts, its, prd

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
