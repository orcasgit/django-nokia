import os

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_nokia',
    }
}
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'nokiaapp',
]
SECRET_KEY = 'something-secret'
ROOT_URLCONF = 'nokiaapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(PROJECT_PATH, 'nokiaapp', 'templates'),
            os.path.join(PROJECT_PATH, 'nokiaapp', 'tests', 'templates')
        ],
    },
]

NOKIA_CLIENT_ID = 'fakeid'
NOKIA_CONSUMER_SECRET = 'fakesecret'
NOKIA_SUBSCRIBE = True
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
        'nokiaapp.tasks': {'handlers': ['null'], 'level': 'DEBUG'},
    },
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
