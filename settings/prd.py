from .base import *  # noqa

DEBUG = False

IDP = 'PRD'  # fake, MTS, ITS, PRD

ALLOWED_HOSTS = ['dev.boac.lef']  # TODO

# ToDo: create db settings:
# `cp local.py.example local.py`

try:
    from .local import *
except ImportError:
    pass
