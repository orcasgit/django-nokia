import datetime

from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.utils import timezone
from freezegun import freeze_time
from nokia import NokiaApi, NokiaAuth, NokiaCredentials

from nokiaapp import utils
from nokiaapp.decorators import nokia_integration_warning
from nokiaapp.models import NokiaUser, MeasureGroup, Measure

from .base import NokiaTestBase

try:
    from unittest import mock
except ImportError:  # Python 2.x fallback
    import mock


class TestIntegrationUtility(NokiaTestBase):

    def test_is_integrated(self):
        """Users with stored OAuth information are integrated."""
        self.assertTrue(utils.is_integrated(self.user))

    def test_is_not_integrated(self):
        """User is not integrated if we have no OAuth data for them."""
        NokiaUser.objects.all().delete()
        self.assertFalse(utils.is_integrated(self.user))

    def test_unauthenticated(self):
        """User is not integrated if they aren't logged in."""
        user = AnonymousUser()
        self.assertFalse(utils.is_integrated(user))


class TestIntegrationDecorator(NokiaTestBase):

    def setUp(self):
        super(TestIntegrationDecorator, self).setUp()
        self.fake_request = HttpRequest()
        self.fake_request.user = self.user
        self.fake_view = lambda request: "hello"
        self.messages = []

    def _mock_decorator(self, msg=None):
        def mock_error(request, message, *args, **kwargs):
            self.messages.append(message)

        with mock.patch.object(messages, 'error', mock_error):
            return nokia_integration_warning(msg=msg)(self.fake_view)(
                self.fake_request)

    def test_unauthenticated(self):
        """Message should be added if user is not logged in."""
        self.fake_request.user = AnonymousUser()
        results = self._mock_decorator()

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0],
                         utils.get_setting('NOKIA_DECORATOR_MESSAGE'))

    def test_is_integrated(self):
        """Decorator should have no effect if user is integrated."""
        results = self._mock_decorator()

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 0)

    def test_is_not_integrated(self):
        """Message should be added if user is not integrated."""
        NokiaUser.objects.all().delete()
        results = self._mock_decorator()

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0],
                         utils.get_setting('NOKIA_DECORATOR_MESSAGE'))

    def test_custom_msg(self):
        """Decorator should support a custom message string."""
        NokiaUser.objects.all().delete()
        msg = "customized"
        results = self._mock_decorator(msg)

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0], "customized")

    def test_custom_msg_func(self):
        """Decorator should support a custom message function."""
        NokiaUser.objects.all().delete()

        def msg(request):
            return "message to {0}".format(request.user)
        results = self._mock_decorator(msg)

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0], msg(self.fake_request))


class TestLoginView(NokiaTestBase):
    url_name = 'nokia-login'

    def setUp(self):
        super(TestLoginView, self).setUp()
        NokiaAuth.get_authorize_url = mock.MagicMock(return_value='/test')

    def test_get(self):
        """
        Login view should redirect to an authorization URL and create a user
        """
        response = self._get()
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(NokiaUser.objects.count(), 1)

    def test_unauthenticated(self):
        """User must be logged in to access Login view."""
        self.client.logout()
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NokiaUser.objects.count(), 1)

    def test_unintegrated(self):
        """Nokia credentials not required to access Login view."""
        self.nokia_user.delete()
        response = self._get()
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(NokiaUser.objects.count(), 0)

    def test_next(self):
        response = self._get(get_kwargs={'next': '/next'})
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(
            self.client.session.get('nokia_next', None), '/next')
        self.assertEqual(NokiaUser.objects.count(), 1)


class TestCompleteView(NokiaTestBase):
    url_name = 'nokia-complete'
    access_token = 'abc'
    token_expiry = int((
        datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    ).total_seconds()) + 10
    token_type = 'Bearer'
    refresh_token = '123'
    nokia_user_id = 1111111

    def setUp(self):
        super(TestCompleteView, self).setUp()
        self.nokia_user.delete()

    def _get(self, use_code=True, **kwargs):
        NokiaApi.get_user = mock.MagicMock(return_value=self.get_user)
        NokiaApi.get_measures = mock.MagicMock(
            return_value=self.get_measures)
        NokiaApi.subscribe = mock.MagicMock(return_value=None)
        NokiaAuth.get_credentials = mock.MagicMock(
            return_value=NokiaCredentials(
                access_token=self.access_token,
                token_expiry=self.token_expiry,
                token_type=self.token_type,
                refresh_token=self.refresh_token,
                user_id=self.nokia_user_id))
        get_kwargs = {}
        if use_code:
            get_kwargs['code']  = 'fakecode'
        get_kwargs.update(kwargs.pop('get_kwargs', {}))
        return super(TestCompleteView, self)._get(
            get_kwargs=get_kwargs, **kwargs)

    def test_get(self):
        """
        Complete view should fetch & store user's access credentials, add the
        user's profile to the session, and retrieve all past body measures.
        """
        self.assertEqual(MeasureGroup.objects.count(), 0)
        self.assertEqual(Measure.objects.count(), 0)
        response = self._get()
        self.assertRedirectsNoFollow(
            response, utils.get_setting('NOKIA_LOGIN_REDIRECT'))
        nokia_user = NokiaUser.objects.get()
        self.assertEqual(NokiaApi.get_user.call_count, 1)
        NokiaApi.get_user.assert_called_once_with()
        self.assertEqual(NokiaApi.subscribe.call_count, 2)
        NokiaApi.subscribe.assert_has_calls([
            mock.call('http://testserver/notification/%s/' % appli,
                      'django-nokia', appli=appli) for appli in [1, 4]
        ])
        self.assertEqual(nokia_user.user, self.user)
        self.assertEqual(nokia_user.access_token, self.access_token)
        self.assertEqual(nokia_user.token_expiry, self.token_expiry)
        self.assertEqual(nokia_user.token_type, self.token_type)
        self.assertEqual(nokia_user.refresh_token, self.refresh_token)
        self.assertEqual(nokia_user.nokia_user_id, self.nokia_user_id)
        NokiaApi.get_measures.assert_called_once_with()
        self.assertEqual(MeasureGroup.objects.count(), 3)
        self.assertEqual(Measure.objects.count(), 5)

    def test_unauthenticated(self):
        """User must be logged in to access Complete view."""
        self.client.logout()
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NokiaUser.objects.count(), 0)

    @freeze_time("2012-01-14T12:00:01", tz_offset=0)
    def test_next(self):
        """
        Complete view should redirect to session['nokia_next'] if available.
        """
        self._set_session_vars(nokia_next='/test')
        response = self._get()
        self.assertRedirectsNoFollow(response, '/test')
        nokia_user = NokiaUser.objects.get()
        self.assertEqual(nokia_user.user, self.user)
        self.assertEqual(nokia_user.access_token, self.access_token)
        self.assertEqual(nokia_user.token_expiry, self.token_expiry)
        self.assertEqual(nokia_user.token_type, self.token_type)
        self.assertEqual(nokia_user.refresh_token, self.refresh_token)
        self.assertEqual(nokia_user.last_update, timezone.now())
        self.assertEqual(nokia_user.nokia_user_id, self.nokia_user_id)

    def test_no_code(self):
        """Complete view should redirect to error if code isn't available."""
        response = self._get(use_code=False)

        self.assertRedirectsNoFollow(response, reverse('nokia-error'))
        self.assertEqual(NokiaUser.objects.count(), 0)
        
        # import pdb; pdb.set_trace()
        response = self._get(get_kwargs={'code': ''})

        self.assertRedirectsNoFollow(response, reverse('nokia-error'))
        self.assertEqual(NokiaUser.objects.count(), 0)

    @freeze_time("2012-01-14T12:00:01", tz_offset=0)
    def test_integrated(self):
        """
        Complete view should overwrite existing credentials for this user.
        """
        self.nokia_user = self.create_nokia_user(user=self.user)
        response = self._get()
        nokia_user = NokiaUser.objects.get()
        self.assertEqual(nokia_user.user, self.user)
        self.assertEqual(nokia_user.access_token, self.access_token)
        self.assertEqual(nokia_user.token_expiry, self.token_expiry)
        self.assertEqual(nokia_user.token_type, self.token_type)
        self.assertEqual(nokia_user.refresh_token, self.refresh_token)
        self.assertEqual(nokia_user.last_update, timezone.now())
        self.assertEqual(nokia_user.nokia_user_id, self.nokia_user_id)
        self.assertRedirectsNoFollow(
            response, utils.get_setting('NOKIA_LOGIN_REDIRECT'))


class TestErrorView(NokiaTestBase):
    url_name = 'nokia-error'

    def test_get(self):
        """Should be able to retrieve Error page."""
        response = self._get()
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated(self):
        """User must be logged in to access Error view."""
        self.client.logout()
        response = self._get()
        self.assertEqual(response.status_code, 302)

    def test_unintegrated(self):
        """No Nokia credentials required to access Error view."""
        self.nokia_user.delete()
        response = self._get()
        self.assertEqual(response.status_code, 200)


class TestLogoutView(NokiaTestBase):
    url_name = 'nokia-logout'

    def setUp(self):
        super(TestLogoutView, self).setUp()
        NokiaApi.list_subscriptions = mock.MagicMock(return_value=[{
            'comment': 'django-nokia',
            'expires': 2147483647,
            'appli': 1,
            'callbackurl': 'http://testserver/notification/1/',
        }, {
            'comment': 'django-nokia',
            'expires': 2147483647,
            'appli': 4,
            'callbackurl': 'http://testserver/notification/4/',
        }])
        NokiaApi.unsubscribe = mock.MagicMock(return_value=None)

    def test_get(self):
        """Logout view should remove associated NokiaUser and redirect."""
        response = self._get()
        NokiaApi.list_subscriptions.assert_called_once_with()
        self.assertEqual(NokiaApi.unsubscribe.call_count, 2)
        NokiaApi.unsubscribe.assert_has_calls([
            mock.call('http://testserver/notification/%s/' % appli,
                      appli=appli) for appli in [1, 4]
        ])
        self.assertRedirectsNoFollow(response,
                                     utils.get_setting('NOKIA_LOGIN_REDIRECT'))
        self.assertEqual(NokiaUser.objects.count(), 0)

    def test_unauthenticated(self):
        """User must be logged in to access Logout view."""
        self.client.logout()
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NokiaUser.objects.count(), 1)

    def test_unintegrated(self):
        """No Nokia credentials required to access Logout view."""
        self.nokia_user.delete()
        response = self._get()
        self.assertRedirectsNoFollow(response,
                                     utils.get_setting('NOKIA_LOGIN_REDIRECT'))
        self.assertEqual(NokiaUser.objects.count(), 0)

    def test_next(self):
        """Logout view should redirect to GET['next'] if available."""
        response = self._get(get_kwargs={'next': '/test'})
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(NokiaUser.objects.count(), 0)
