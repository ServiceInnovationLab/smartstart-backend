from os.path import dirname, abspath
from path import Path

BASE_DIR = Path(dirname(dirname(abspath(__file__))))
PROJ_NAME = 'smartstart'
LOG_FILE_NAME = '{}.log'.format(PROJ_NAME)

ADMINS = [
    ('lef-system', 'lef-system@catalyst.net.nz'),
]

MANAGERS = ADMINS

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

     'django_otp',
     'django_otp.plugins.otp_totp',
     # 'django_otp.plugins.otp_hotp',
     'django_otp.plugins.otp_static',
     # 'django_otp.plugins.otp_email',
     'two_factor',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # above all except SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.accounts.middleware.UserCookieMiddleWare',
    'apps.accounts.middleware.Check2FAMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR/'templates',
        ],
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

# used by Django Admin
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/'

# email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_PORT = 587

EMAIL_HOST = 'aws-email-host'
EMAIL_HOST_USER = 'aws-email-user-key'
EMAIL_HOST_PASSWORD = 'aws-email-user-password'

DEFAULT_FROM_EMAIL = 'from-email'

REPLY_TO_EMAIL = 'reply-to-email'
RETURN_PATH_EMAIL = 'return-path-email'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  '/tmp/{}.db'.format(PROJ_NAME)
    }
}


BUNDLES_ROOT = BASE_DIR / 'bundles'
STATIC_ROOT = BASE_DIR / 'static'
LOG_FILE_PATH = BASE_DIR / LOG_FILE_NAME
FORCE_2FA = True
# cookie to exchange info between backend and frontend
EXCHANGE_COOKIE_NAME = 'is_authenticated'


############# BEGIN OVERRIDE #############
# settings may need to override in local.py
# principle: use production as default if possible
DEBUG = False
SESSION_COOKIE_AGE = 30 * 60  # 30 mins

SITE_DOMAIN = 'smartstart.services.govt.nz'
SITE_URL = 'https://{}'.format(SITE_DOMAIN)

BUNDLE_NAME = 'PRD'  # MTS, ITE-uat, ITE-testing, PRD

############# END OVERRIDE #############

try:
    from .local import *  # noqa
except ImportError:
    pass

SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = SITE_URL.startswith('https')

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
            'filename': LOG_FILE_PATH,
            'formatter': 'simple',
            'maxBytes': 10 * 1024 * 1024,  # 10 mb
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARN',
        },
        'apps': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'handlers': ['console', 'file'],
        },
    },
}

# realme bundles settings, must be after local since we need SITE_URL here
BUNDLES = {
    'MTS': {
        'idp_entity_id': 'https://mts.realme.govt.nz/saml2',
        'sp_entity_id': '{}/sp/mts'.format(SITE_URL.strip('/')),
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
