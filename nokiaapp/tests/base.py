from mock import patch, Mock
import random
try:
    from urllib.parse import urlencode
    from string import ascii_letters
except:
    # Python 2.x
    from urllib import urlencode
    from string import letters as ascii_letters

import django
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from nokia import NokiaApi, NokiaCredentials, NokiaMeasures

from nokiaapp.models import NokiaUser


class NokiaTestBase(TestCase):
    TEST_SERVER = 'http://testserver'

    def setUp(self):
        self.username = self.random_string(25)
        self.password = self.random_string(25)
        self.user = self.create_user(username=self.username,
                                     password=self.password)
        self.nokia_user = self.create_nokia_user(user=self.user)
        self.get_user = {
            'id': 1111111, 'birthdate': 364305600, 'lastname': 'Baggins',
            'ispublic': 255, 'firstname': 'Frodo', 'fatmethod': 131}
        self.get_measures = NokiaMeasures({
            "updatetime": 1249409679,
            "measuregrps": [{
                "grpid": 2909,
                "attrib": 0,
                "date": 1222930968,
                "category": 1,
                "measures": [{
                    "value": 79300,
                    "type": 1,
                    "unit": -3
                }]
            }, {
                "grpid": 2910,
                "attrib": 1,
                "date": 1222930968,
                "category": 1,
                "measures": [{
                    "value": 652,
                    "type": 5,
                    "unit": -1
                }, {
                    "value": 178,
                    "type": 6,
                    "unit": -1
                }, {
                    "value": 14125,
                    "type": 8,
                    "unit": -3
                }]
            },
            {
                "grpid": 2908,
                "attrib": 0,
                "date": 1222930968,
                "category": 1,
                "measures": [{
                    "value": 173,
                    "type": 4,
                    "unit": -2
                }]
            }]
        })

        self.client.login(username=self.username, password=self.password)

    def random_string(self, length=255, extra_chars=''):
        chars = ascii_letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

    def create_user(self, username=None, email=None, password=None, **kwargs):
        username = username or self.random_string(25)
        email = email or '{0}@{1}.com'.format(self.random_string(25),
                                              self.random_string(10))
        password = password or self.random_string(25)
        user = User.objects.create_user(username, email, password)
        User.objects.filter(pk=user.pk).update(**kwargs)
        user = User.objects.get(pk=user.pk)
        return user

    def create_nokia_user(self, **kwargs):
        defaults = {
            'user': kwargs.pop('user', self.create_user()),
            'nokia_user_id': random.randint(111111, 999999),
            'access_token': self.random_string(25),
            'access_token_secret': self.random_string(25),
        }
        defaults.update(kwargs)
        return NokiaUser.objects.create(**defaults)

    def assertRedirectsNoFollow(self, response, url, status_code=302):
        """
        Workaround to test whether a response redirects to another URL without
        loading the page at that URL.
        """
        self.assertEqual(response.status_code, status_code)
        full_url = (self.TEST_SERVER if django.VERSION < (1, 9,) else '') + url
        self.assertEqual(response._headers['location'][1], full_url)

    def _get(self, url_name=None, url_kwargs=None, get_kwargs=None, **kwargs):
        """Convenience wrapper for test client GET request."""
        url_name = url_name or self.url_name
        url = reverse(url_name, kwargs=url_kwargs)  # Base URL.

        # Add GET parameters.
        if get_kwargs:
            url += '?' + urlencode(get_kwargs)

        return self.client.get(url, **kwargs)

    def _set_session_vars(self, **kwargs):
        session = self.client.session
        for key, value in kwargs.items():
            session[key] = value
        try:
            session.save()  # Only available on authenticated sessions.
        except AttributeError:
            pass

    def _error_response(self):
        error_response = Mock(['content'])
        error_response.content = '{"errors": []}'.encode('utf8')
        return error_response

    @patch('nokiaapp.utils.get_nokia_data')
    def _mock_utility(self, utility=None, error=None, response=None, **kwargs):
        if error:
            utility.side_effect = error(self._error_response())
        elif response:
            utility.return_value = response
        return self._get(**kwargs)
