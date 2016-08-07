from .base import *  # noqa

DEBUG = False

SESSION_COOKIE_SECURE = True

IDP = 'PRD'  # FAKE, MTS, ITE-uat, ITE-testing, PRD

ALLOWED_HOSTS = ['*.dev.boac.lef']  # TODO

# ToDo: create db settings:
# `cp local.py.example local.py`

try:
    from .local import *
except ImportError:
    pass
