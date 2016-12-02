# copy this file to local.py and edit

# example for dev
DEBUG = True
SITE_DOMAIN = '127.0.0.1:8000'
SITE_URL = 'http://{}'.format(SITE_DOMAIN)
BUNDLE_NAME = 'MTS'  # FAKE, MTS, ITE-uat, ITE-testing, PRD

# example for prd
BUNDLES_ROOT = '/srv/bundles'
LOG_FILE_PATH = '/var/log/smartstart.log'
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

