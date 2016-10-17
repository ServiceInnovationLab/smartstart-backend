# copy this file to local.py and edit

# example for dev
BUNDLES_ROOT = '/home/joeg/lef/ops/files/bundles'

SITE_URL = 'https://joeg.dev.boac.lef'

BUNDLE_NAME = 'MTS'  # FAKE, MTS, ITE-uat, ITE-testing, PRD

# example for prd
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

