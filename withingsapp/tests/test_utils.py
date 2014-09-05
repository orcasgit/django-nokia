from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from withings import WithingsApi

from withingsapp.utils import create_withings, get_setting


class TestWithingsUtilities(TestCase):
    def test_create_withings(self):
        """
        Check that the create_withings utility creates a WithingnsApi object
        and an error is raised when the consumer key or secret aren't set.
        """
        with self.settings(WITHINGS_CONSUMER_KEY=None,
                           WITHINGS_CONSUMER_SECRET=None):
            self.assertRaises(ImproperlyConfigured, create_withings)
        with self.settings(WITHINGS_CONSUMER_KEY='',
                           WITHINGS_CONSUMER_SECRET=None):
            self.assertRaises(ImproperlyConfigured, create_withings)
        with self.settings(WITHINGS_CONSUMER_KEY=None,
                           WITHINGS_CONSUMER_SECRET=''):
            self.assertRaises(ImproperlyConfigured, create_withings)
        api = create_withings()
        self.assertEqual(type(api), WithingsApi)
        self.assertEqual(api.credentials.consumer_key,
                         get_setting('WITHINGS_CONSUMER_KEY'))
        self.assertEqual(api.credentials.consumer_secret,
                         get_setting('WITHINGS_CONSUMER_SECRET'))

    def test_get_setting_error(self):
        """
        Check that an error is raised when trying to get a nonexistent setting.
        """
        self.assertRaises(ImproperlyConfigured, get_setting, 'DOES_NOT_EXIST')
