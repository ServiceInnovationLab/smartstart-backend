from .base import *  # noqa

DEBUG = False

AUTH_METHOD = 'prd'  # fake, mts, its, prd

ALLOWED_HOSTS = ['dev.boac.lef']  # TODO

# ToDo: create db settings:
# `cp local.py.example local.py`

try:
    from .local import *
except ImportError:
    pass

