# Copy this file to local.py and edit.

# Example development settings:
DEBUG = True
SITE_DOMAIN = '127.0.0.1:8000'
SITE_URL = 'http://{}'.format(SITE_DOMAIN)
BUNDLE_NAME = 'MTS'  # FAKE, MTS, ITE-uat, ITE-testing, PRD

# Add valid PostgreSQL database details here. Smartstart relies on the
# PostgreSQL JSON field type, and no longer works with SQLite.
# Refer to the Django DATABASES setting in the documentation:
#    https://docs.djangoproject.com/en/1.11/ref/settings/#databases
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

# Example production settings:
BUNDLES_ROOT = '/srv/bundles'
LOG_FILE_PATH = '/var/log/smartstart.log'
# SECRET_KEY = 'a long, random and unique hash string'
# REQUEST_CACHE_TTL = timedelta(minutes=10)
