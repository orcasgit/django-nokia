#!/usr/bin/env python

import coverage
import optparse
import os
import sys

from celery import Celery
from django.conf import settings

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'django_withings',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sessions',
            'withingsapp',
        ],
        SECRET_KEY='something-secret',
        ROOT_URLCONF='withingsapp.urls',

        TEMPLATE_DIRS=(
            os.path.join(PROJECT_PATH, 'withingsapp', 'templates'),
            os.path.join(PROJECT_PATH, 'withingsapp', 'tests', 'templates'),),

        WITHINGS_CONSUMER_KEY='',
        WITHINGS_CONSUMER_SECRET='',
        WITHINGS_SUBSCRIBE=True,

        LOGGING = {
            'version': 1,
            'handlers': {
                'null': {
                    'level': 'DEBUG',
                    'class': 'django.utils.log.NullHandler',
                },
            },
            'loggers': {
                'withingsapp.tasks': {'handlers': ['null'], 'level': 'DEBUG'},
            },
        },

        MIDDLEWARE_CLASSES = (
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        )
    )


from django.test.utils import get_runner


def run_tests():
    parser = optparse.OptionParser()
    parser.add_option('--coverage', dest='coverage', default='2',
                      help="coverage level, 0=no coverage, 1=without branches,"
                      " 2=with branches")
    options, tests = parser.parse_args()
    tests = tests or ['withingsapp']

    covlevel = int(options.coverage)
    if covlevel:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if covlevel == 2:
            branch = True
        else:
            branch = False
        cov = coverage.coverage(branch=branch, config_file='.coveragerc')
        cov.load()
        cov.start()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    exit_val = test_runner.run_tests(tests)

    if covlevel:
        cov.stop()
        cov.save()

    sys.exit(exit_val)


import django
# In Django 1.7, we need to run setup first
if hasattr(django, 'setup'):
    django.setup()


if __name__ == '__main__':
    run_tests()
