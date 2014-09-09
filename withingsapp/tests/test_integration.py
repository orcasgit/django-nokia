from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from withings import WithingsApi, WithingsAuth, WithingsCredentials

from withingsapp import utils
from withingsapp.decorators import withings_integration_warning
from withingsapp.models import WithingsUser, MeasureGroup, Measure

from .base import WithingsTestBase

try:
    from unittest import mock
except ImportError:  # Python 2.x fallback
    import mock


class TestIntegrationUtility(WithingsTestBase):

    def test_is_integrated(self):
        """Users with stored OAuth information are integrated."""
        self.assertTrue(utils.is_integrated(self.user))

    def test_is_not_integrated(self):
        """User is not integrated if we have no OAuth data for them."""
        WithingsUser.objects.all().delete()
        self.assertFalse(utils.is_integrated(self.user))

    def test_unauthenticated(self):
        """User is not integrated if they aren't logged in."""
        user = AnonymousUser()
        self.assertFalse(utils.is_integrated(user))


class TestIntegrationDecorator(WithingsTestBase):

    def setUp(self):
        super(TestIntegrationDecorator, self).setUp()
        self.fake_request = HttpRequest()
        self.fake_request.user = self.user
        self.fake_view = lambda request: "hello"
        self.messages = []

    def _mock_decorator(self, msg=None):
        def mock_error(request, message, *args, **kwargs):
            self.messages.append(message)

        with mock.patch.object(messages, 'error', mock_error) as error:
            return withings_integration_warning(msg=msg)(self.fake_view)(
                self.fake_request)

    def test_unauthenticated(self):
        """Message should be added if user is not logged in."""
        self.fake_request.user = AnonymousUser()
        results = self._mock_decorator()

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0],
                utils.get_setting('WITHINGS_DECORATOR_MESSAGE'))

    def test_is_integrated(self):
        """Decorator should have no effect if user is integrated."""
        results = self._mock_decorator()

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 0)

    def test_is_not_integrated(self):
        """Message should be added if user is not integrated."""
        WithingsUser.objects.all().delete()
        results = self._mock_decorator()

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0],
                utils.get_setting('WITHINGS_DECORATOR_MESSAGE'))

    def test_custom_msg(self):
        """Decorator should support a custom message string."""
        WithingsUser.objects.all().delete()
        msg = "customized"
        results = self._mock_decorator(msg)

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0], "customized")

    def test_custom_msg_func(self):
        """Decorator should support a custom message function."""
        WithingsUser.objects.all().delete()
        msg = lambda request: "message to {0}".format(request.user)
        results = self._mock_decorator(msg)

        self.assertEqual(results, "hello")
        self.assertEqual(len(self.messages), 1)
        self.assertEqual(self.messages[0], msg(self.fake_request))


class TestLoginView(WithingsTestBase):
    url_name = 'withings-login'

    def setUp(self):
        super(TestLoginView, self).setUp()
        WithingsAuth.get_authorize_url = mock.MagicMock(return_value='/test')

    def test_get(self):
        """
        Login view should generate & store a request token then
        redirect to an authorization URL.
        """
        response = self._get()
        self.assertRedirectsNoFollow(response, '/test')
        self.assertTrue('oauth_token' in self.client.session)
        self.assertTrue('oauth_secret' in self.client.session)
        self.assertEqual(WithingsUser.objects.count(), 1)

    def test_unauthenticated(self):
        """User must be logged in to access Login view."""
        self.client.logout()
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WithingsUser.objects.count(), 1)

    def test_unintegrated(self):
        """Withings credentials not required to access Login view."""
        self.withings_user.delete()
        response = self._get()
        self.assertRedirectsNoFollow(response, '/test')
        self.assertTrue('oauth_token' in self.client.session)
        self.assertTrue('oauth_secret' in self.client.session)
        self.assertEqual(WithingsUser.objects.count(), 0)

    def test_next(self):
        response = self._get(get_kwargs={'next': '/next'})
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(
            self.client.session.get('withings_next', None), '/next')
        self.assertEqual(WithingsUser.objects.count(), 1)


class TestCompleteView(WithingsTestBase):
    url_name = 'withings-complete'
    access_token = 'abc'
    access_token_secret = '123'
    withings_user_id = 1111111

    def setUp(self):
        super(TestCompleteView, self).setUp()
        self.withings_user.delete()

    def _get(self, use_token=True, use_verifier=True, **kwargs):
        WithingsApi.get_user = mock.MagicMock(return_value=self.get_user)
        WithingsApi.get_measures = mock.MagicMock(
            return_value=self.get_measures)
        WithingsApi.subscribe = mock.MagicMock(return_value=None)
        WithingsAuth.get_credentials = mock.MagicMock(
            return_value=WithingsCredentials(
                access_token=self.access_token,
                access_token_secret=self.access_token_secret))
        if use_token:
            self._set_session_vars(oauth_token=self.access_token,
                                   oauth_secret=self.access_token_secret)
        get_kwargs = kwargs.pop('get_kwargs', {})
        if use_verifier:
            get_kwargs.update({'oauth_verifier': 'verifier',
                               'userid': self.withings_user_id})
        return super(TestCompleteView, self)._get(get_kwargs=get_kwargs,
                                                  **kwargs)

    def test_get(self):
        """
        Complete view should fetch & store user's access credentials, add the
        user's profile to the session, and retrieve all past body measures.
        """
        self.assertEqual(MeasureGroup.objects.count(), 0)
        self.assertEqual(Measure.objects.count(), 0)
        response = self._get()
        self.assertRedirectsNoFollow(
            response, utils.get_setting('WITHINGS_LOGIN_REDIRECT'))
        withings_user = WithingsUser.objects.get()
        self.assertEqual(WithingsApi.get_user.call_count, 1)
        WithingsApi.get_user.assert_called_once_with()
        self.assertEqual(WithingsApi.subscribe.call_count, 2)
        WithingsApi.subscribe.assert_has_calls([
            mock.call('http://testserver/notification/%s/' % appli,
                      'django-withings', appli=appli) for appli in [1, 4]
        ])
        self.assertEqual(withings_user.user, self.user)
        self.assertEqual(withings_user.access_token, self.access_token)
        self.assertEqual(withings_user.access_token_secret,
                         self.access_token_secret)
        self.assertEqual(withings_user.withings_user_id, self.withings_user_id)
        WithingsApi.get_measures.assert_called_once_with()
        self.assertEqual(MeasureGroup.objects.count(), 3)
        self.assertEqual(Measure.objects.count(), 5)

    def test_unauthenticated(self):
        """User must be logged in to access Complete view."""
        self.client.logout()
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WithingsUser.objects.count(), 0)

    def test_next(self):
        """
        Complete view should redirect to session['withings_next'] if available.
        """
        self._set_session_vars(withings_next='/test')
        response = self._get()
        self.assertRedirectsNoFollow(response, '/test')
        withings_user = WithingsUser.objects.get()
        self.assertEqual(withings_user.user, self.user)
        self.assertEqual(withings_user.access_token, self.access_token)
        self.assertEqual(withings_user.access_token_secret,
                         self.access_token_secret)
        self.assertEqual(withings_user.withings_user_id, self.withings_user_id)

    def test_no_token(self):
        """Complete view should redirect to error if token isn't in session."""
        response = self._get(use_token=False)
        self.assertRedirectsNoFollow(response, reverse('withings-error'))
        self.assertEqual(WithingsUser.objects.count(), 0)

    def test_no_verifier(self):
        """
        Complete view should redirect to error if verifier param is not
        present.
        """
        response = self._get(use_verifier=False)
        self.assertRedirectsNoFollow(response, reverse('withings-error'))
        self.assertEqual(WithingsUser.objects.count(), 0)

    def test_integrated(self):
        """
        Complete view should overwrite existing credentials for this user.
        """
        self.withings_user = self.create_withings_user(user=self.user)
        response = self._get()
        withings_user = WithingsUser.objects.get()
        self.assertEqual(withings_user.user, self.user)
        self.assertEqual(withings_user.access_token, self.access_token)
        self.assertEqual(withings_user.access_token_secret,
                         self.access_token_secret)
        self.assertEqual(withings_user.withings_user_id, self.withings_user_id)
        self.assertRedirectsNoFollow(
            response, utils.get_setting('WITHINGS_LOGIN_REDIRECT'))


class TestErrorView(WithingsTestBase):
    url_name = 'withings-error'

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
        """No Withings credentials required to access Error view."""
        self.withings_user.delete()
        response = self._get()
        self.assertEqual(response.status_code, 200)


class TestLogoutView(WithingsTestBase):
    url_name = 'withings-logout'

    def setUp(self):
        super(TestLogoutView, self).setUp()
        WithingsApi.list_subscriptions = mock.MagicMock(return_value=[
            {'comment': 'django-withings', 'expires': 2147483647}])
        WithingsApi.unsubscribe = mock.MagicMock(return_value=None)

    def test_get(self):
        """Logout view should remove associated WithingsUser and redirect."""
        response = self._get()
        self.assertEqual(WithingsApi.list_subscriptions.call_count, 2)
        WithingsApi.list_subscriptions.assert_has_calls([
            mock.call(appli=appli) for appli in [1, 4]
        ])
        self.assertEqual(WithingsApi.unsubscribe.call_count, 2)
        WithingsApi.unsubscribe.assert_has_calls([
            mock.call('http://testserver/notification/%s/' % appli,
                      appli=appli) for appli in [1, 4]
        ])
        self.assertRedirectsNoFollow(response,
            utils.get_setting('WITHINGS_LOGIN_REDIRECT'))
        self.assertEqual(WithingsUser.objects.count(), 0)

    def test_unauthenticated(self):
        """User must be logged in to access Logout view."""
        self.client.logout()
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WithingsUser.objects.count(), 1)

    def test_unintegrated(self):
        """No Withings credentials required to access Logout view."""
        self.withings_user.delete()
        response = self._get()
        self.assertRedirectsNoFollow(response,
            utils.get_setting('WITHINGS_LOGIN_REDIRECT'))
        self.assertEqual(WithingsUser.objects.count(), 0)

    def test_next(self):
        """Logout view should redirect to GET['next'] if available."""
        response = self._get(get_kwargs={'next': '/test'})
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(WithingsUser.objects.count(), 0)
