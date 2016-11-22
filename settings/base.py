from os.path import dirname, abspath
from path import path

BASE_DIR = path(dirname(dirname(abspath(__file__))))
PROJ_NAME = 'smartstart'

USE_I18N = True

USE_L10N = True

LANGUAGE_CODE = 'en-nz'

USE_TZ = True

TIME_ZONE = 'Pacific/Auckland'

STATIC_URL = '/static/'

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

SECRET_KEY = 'ne-oa++#f(*a=@f-5bd0$6406z8vej3@&gf(ry_d%mxd@@s9i#'

# django loads templates in apps installed order,
# so it's good to put our own apps first
# that we can override templates of other apps.
# e.g.: login.html in apps.accounts will override the one in rest_framework.

INSTALLED_APPS = [
    # our own apps
    'apps.base',
    'apps.accounts',
    'apps.realme',
    'apps.timeline',

    # 3rd party apps
    'django_extensions',
    'rest_framework',

    # django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # above all except SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.accounts.middleware.UserCookieMiddleWare',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.SessionAuthentication',
        'apps.accounts.authentication.FixedSessionAuthentication',
    ),
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'apps.realme.backends.SamlBackend',
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

BUNDLES = {
    'MTS': {
        'idp_entity_id': 'https://mts.realme.govt.nz/saml2',
        'sp_entity_id': 'https://bundle.services.govt.nz/sp/mts',
        'saml_idp_cer': 'mts_login_saml_idp.cer',
        'mutual_ssl_idp_cer': 'mts_mutual_ssl_idp.cer',
        'single_sign_on_service': 'https://mts.realme.govt.nz/logon-mts/mtsEntryPoint',
        'seamless_logon_service': 'NA',
        'saml_sp_cer': 'mts_saml_sp.cer',
        'saml_sp_key': 'mts_saml_sp.key',
        'mutual_ssl_sp_cer': 'mts_mutual_ssl_sp.cer',
        'mutual_ssl_sp_key': 'mts_mutual_ssl_sp.key',
    },
    'ITE-uat': {
        'idp_entity_id': 'https://www.ite.logon.realme.govt.nz/saml2',
        'sp_entity_id': 'https://bundle.services.govt.nz/sp/uat',
        'saml_idp_cer': 'ite.signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.ite.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.ite.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'seamless_logon_service': 'https://www.ite.logon.realme.govt.nz/cls/seamlessEndpoint',
        'site_url': 'https://uat.smartstart.services.govt.nz',
        'saml_sp_cer': 'ite.sa.saml.sig.uat.bundle.services.govt.nz.crt',
        'saml_sp_key': 'ite.sa.saml.sig.uat.bundle.services.govt.nz.private.key',
        'mutual_ssl_sp_cer': 'ite.sa.mutual.sig.uat.bundle.services.govt.nz.crt',
        'mutual_ssl_sp_key': 'ite.sa.mutual.sig.uat.bundle.services.govt.nz.private.key',
    },
    'ITE-testing': {
        'idp_entity_id': 'https://www.ite.logon.realme.govt.nz/saml2',
        'sp_entity_id': 'https://bundle.services.govt.nz/sp/testing',
        'saml_idp_cer': 'ite.signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.ite.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.ite.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'seamless_logon_service': 'https://www.ite.logon.realme.govt.nz/cls/seamlessEndpoint',
        'site_url': 'https://testing.smartstart.services.govt.nz',
        'saml_sp_cer': 'ite.sa.saml.sig.testing.bundle.services.govt.nz.crt',
        'saml_sp_key': 'ite.sa.saml.sig.testing.bundle.services.govt.nz.private.key',
        'mutual_ssl_sp_cer': 'ite.sa.mutual.sig.testing.bundle.services.govt.nz.crt',
        'mutual_ssl_sp_key': 'ite.sa.mutual.sig.testing.bundle.services.govt.nz.private.key',
        'target_sps': {
            'test': {
                'entity_id': 'https://testagency.dia.govt.nz/igovtTargetAgency2/EntityID3',
                'relay_state': 'idpMetaAliasxITE-IDP1/spMetaAliasxITE-SP3/cotxITE',
            }
        }
    },
    'PRD': {
        'idp_entity_id': 'https://www.logon.realme.govt.nz/saml2',
        'sp_entity_id': 'https://smartstart.services.govt.nz/sp/SmartStart',
        'saml_idp_cer': 'signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'seamless_logon_service': 'https://www.logon.realme.govt.nz/cls/seamlessEndpoint',
        'site_url': 'https://smartstart.services.govt.nz',
        'saml_sp_cer': 'prod.sa.saml.sig.smartstart.services.govt.nz.crt',
        'saml_sp_key': 'prod.sa.saml.sig.smartstart.services.govt.nz.private.key',
        'mutual_ssl_sp_cer': '',  # not ready yet
        'mutual_ssl_sp_key': '',  # not ready yet
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  '/tmp/{}.db'.format(PROJ_NAME)
    }
}

BUNDLES_ROOT = BASE_DIR/'bundles'
STATIC_ROOT = BASE_DIR/'static'

############# BEGIN OVERRIDE #############
# settings may need to override in local.py
# principle: use production as default if possible
DEBUG = False
SESSION_COOKIE_AGE = 30 * 60  # 30 mins
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SITE_DOMAIN = 'smartstart.services.govt.nz'
SITE_URL = 'https://{}'.format(SITE_DOMAIN)

BUNDLE_NAME = 'PRD'  # MTS, ITE-uat, ITE-testing, PRD

LOG_FILE = '/var/log/boac.log'

############# END OVERRIDE #############

try:
    from .local import *  # noqa
except ImportError:
    pass

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['.{}'.format(SITE_DOMAIN)]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(funcName)s line %(lineno)s: \n%(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'formatter': 'simple',
            'maxBytes': 10 * 1024 * 1024,  # 10 mb
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARN',
        },
        'apps': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
    },
}

# cookie to exchange info between backend and frontend
EXCHANGE_COOKIE_NAME = 'is_authenticated'
