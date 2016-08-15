from os.path import dirname, abspath
from path import path

BASE_DIR = path(dirname(dirname(abspath(__file__))))

USE_I18N = True

USE_L10N = True

LANGUAGE_CODE = 'en-nz'

USE_TZ = True

TIME_ZONE = 'Pacific/Auckland'

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

SECRET_KEY = 'ne-oa++#f(*a=@f-5bd0$6406z8vej3@&gf(ry_d%mxd@@s9i#'

# django loads templates in apps installed order,
# so it's good to put our own apps first
# that we can override templates of other apps.
# e.g.: login.html in apps.accounts will override the one in rest_framework.

INSTALLED_APPS = [
    # our own apps
    'apps.accounts',
    'apps.sp',

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
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'apps.sp.backends.SamlBackend',
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARN',
        },
        'apps': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}


BUNDLES = {
    'MTS': {
        'idp_entity_id': 'https://mts.realme.govt.nz/saml2',
        'sp_entity_id': 'https://bundle.services.govt.nz/sp/mts',
        'saml_idp_cer': 'mts_login_saml_idp.cer',
        'mutual_ssl_idp_cer': 'mts_mutual_ssl_idp.cer',
        'single_sign_on_service': 'https://mts.realme.govt.nz/logon-mts/mtsEntryPoint',
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
        'site_url': 'https://uat.bundle.services.govt.nz',
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
        'site_url': 'https://testing.bundle.services.govt.nz',
        'saml_sp_cer': 'ite.sa.saml.sig.testing.bundle.services.govt.nz.crt',
        'saml_sp_key': 'ite.sa.saml.sig.testing.bundle.services.govt.nz.private.key',
        'mutual_ssl_sp_cer': 'ite.sa.mutual.sig.testing.bundle.services.govt.nz.crt',
        'mutual_ssl_sp_key': 'ite.sa.mutual.sig.testing.bundle.services.govt.nz.private.key',
    },
    'PRD': {
        'idp_entity_id': 'https://www.logon.realme.govt.nz/saml2',
        'sp_entity_id': 'https://bundle.services.govt.nz/sp/prd',  # TODO: to confirm
        'saml_idp_cer': 'signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'site_url': 'https://bundle.services.govt.nz',
        'saml_sp_cer': 'sa.saml.sig.bundle.services.govt.nz.crt',
        'saml_sp_key': 'sa.saml.sig.bundle.services.govt.nz.private.key',
        'mutual_ssl_sp_cer': 'sa.mutual.sig.bundle.services.govt.nz.crt',
        'mutual_ssl_sp_key': 'sa.mutual.sig.bundle.services.govt.nz.private.key',
    },
}

BUNDLES_ROOT = BASE_DIR.parent/'bundles'
