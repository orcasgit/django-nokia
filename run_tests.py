#!/usr/bin/env python

import coverage
import optparse
import os
import sys

from django.conf import settings
from django.test.utils import get_runner


if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")


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
    test_runner = TestRunner(verbosity=2, interactive=True, failfast=False)
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
