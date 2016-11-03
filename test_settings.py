import os

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_withings',
    }
}
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'withingsapp',
]
SECRET_KEY = 'something-secret'
ROOT_URLCONF = 'withingsapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(PROJECT_PATH, 'withingsapp', 'templates'),
            os.path.join(PROJECT_PATH, 'withingsapp', 'tests', 'templates')
        ],
    },
]

WITHINGS_CONSUMER_KEY = ''
WITHINGS_CONSUMER_SECRET = ''
WITHINGS_SUBSCRIBE = True
USE_TZ = True
TIME_ZONE = 'America/Chicago'

LOGGING = {
    'version': 1,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'withingsapp.tasks': {'handlers': ['null'], 'level': 'DEBUG'},
    },
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
