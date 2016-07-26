import sys
from os.path import dirname, abspath
from path import path

BASE_DIR = path(dirname(dirname(abspath(__file__))))
# sys.path.insert(0, BASE_DIR / 'apps')  # noqa

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
LOGIN_REDIRECT_URL = '/api/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

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
