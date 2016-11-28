# copy this file to local.py and edit

# example for dev
DEBUG = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SITE_DOMAIN = '127.0.0.1:8000'
SITE_URL = 'http://{}'.format(SITE_DOMAIN)
BUNDLE_NAME = 'MTS'  # FAKE, MTS, ITE-uat, ITE-testing, PRD
LOG_FILE = '/tmp/smartstart.log'

# example for prd
BUNDLES_ROOT = '/srv/bundles'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'mydatabaseuser',
        'PASSWORD': 'mypassword',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

