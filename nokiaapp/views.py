import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from . import utils
from .models import NokiaUser, MeasureGroup

try:
    from django.urls import NoReverseMatch
except ImportError:
    # Fallback for older Djangos
    from django.core.urlresolvers import NoReverseMatch

logger = logging.getLogger(__name__)


@login_required
def login(request):
    """
    Begins the OAuth authentication process by obtaining a Request Token from
    Nokia and redirecting the user to the Nokia site for authorization.

    When the user has finished at the Nokia site, they will be redirected
    to the :py:func:`nokiaapp.views.complete` view.

    If 'next' is provided in the GET data, it is saved in the session so the
    :py:func:`nokiaapp.views.complete` view can redirect the user to that
    URL upon successful authentication.

    URL name:
        `nokia-login`
    """
    next_url = request.GET.get('next', None)
    if next_url:
        request.session['nokia_next'] = next_url
    else:
        request.session.pop('nokia_next', None)

    callback_uri = request.build_absolute_uri(reverse('nokia-complete'))
    auth = utils.create_nokia_auth()
    auth_url = auth.get_authorize_url(callback_uri=callback_uri)
    request.session['oauth_token'] = auth.oauth_token
    request.session['oauth_secret'] = auth.oauth_secret
    return redirect(auth_url)


@login_required
def complete(request):
    """
    After the user authorizes us, Nokia sends a callback to this URL to
    complete authentication.

    If there was an error, the user is redirected again to the `error` view.

    If the authorization was successful, the credentials are stored for us to
    use later, and the user is redirected. If 'next_url' is in the request
    session, the user is redirected to that URL. Otherwise, they are
    redirected to the URL specified by the setting
    :ref:`NOKIA_LOGIN_REDIRECT`.

    If :ref:`NOKIA_SUBSCRIBE` is set to True, add a subscription to user
    data at this time.

    URL name:
        `nokia-complete`
    """
    auth = utils.create_nokia_auth()
    try:
        auth.oauth_token = request.session.pop('oauth_token')
        auth.oauth_secret = request.session.pop('oauth_secret')
        verifier = request.GET.get('oauth_verifier')
        user_id = request.GET.get('userid')
    except KeyError:
        return redirect(reverse('nokia-error'))
    if not verifier or not user_id:
        return redirect(reverse('nokia-error'))
    try:
        creds = auth.get_credentials(verifier)
    except:
        return redirect(reverse('nokia-error'))

    user_updates = {
        'access_token': creds.access_token,
        'access_token_secret': creds.access_token_secret,
        'nokia_user_id': user_id,
        'last_update': timezone.now(),
    }
    nokia_user = NokiaUser.objects.filter(user=request.user)
    if nokia_user.exists():
        nokia_user.update(**user_updates)
        nokia_user = nokia_user[0]
    else:
        user_updates['user'] = request.user
        nokia_user = NokiaUser.objects.create(**user_updates)
    # Add the Nokia user info to the session
    api = utils.create_nokia(**nokia_user.get_user_data())
    request.session['nokia_profile'] = api.get_user()
    MeasureGroup.create_from_measures(request.user, api.get_measures())
    if utils.get_setting('NOKIA_SUBSCRIBE'):
        for appli in [1, 4]:
            notification_url = request.build_absolute_uri(
                reverse('nokia-notification', kwargs={'appli': appli}))
            api.subscribe(notification_url, 'django-nokia', appli=appli)

    next_url = request.session.pop('nokia_next', None) or utils.get_setting(
        'NOKIA_LOGIN_REDIRECT')
    return redirect(next_url)


@receiver(user_logged_in)
def create_nokia_session(sender, request, user, **kwargs):
    """ If the user is a Nokia user, update the profile in the session. """

    if (user.is_authenticated() and utils.is_integrated(user) and
            user.is_active):
        nokia_user = NokiaUser.objects.filter(user=user)
        if nokia_user.exists():
            api = utils.create_nokia(**nokia_user[0].get_user_data())
            try:
                request.session['nokia_profile'] = api.get_user()
            except:
                pass


@login_required
def error(request):
    """
    The user is redirected to this view if we encounter an error acquiring
    their Nokia credentials. It renders the template defined in the setting
    :ref:`NOKIA_ERROR_TEMPLATE`. The default template, located at
    *nokia/error.html*, simply informs the user of the error::

        <html>
            <head>
                <title>Nokia Authentication Error</title>
            </head>
            <body>
                <h1>Nokia Authentication Error</h1>

                <p>We encontered an error while attempting to authenticate you
                through Nokia.</p>
            </body>
        </html>

    URL name:
        `nokia-error`
    """
    return render(request, utils.get_setting('NOKIA_ERROR_TEMPLATE'), {})


@login_required
def logout(request):
    """Forget this user's Nokia credentials.

    If the request has a `next` parameter, the user is redirected to that URL.
    Otherwise, they're redirected to the URL defined in the setting
    :ref:`NOKIA_LOGOUT_REDIRECT`.

    URL name:
        `nokia-logout`
    """
    nokia_user = NokiaUser.objects.filter(user=request.user)
    urls = []
    for appli in [1, 4]:
        for app in ['nokia', 'withings']:
            try:
                urls.append(request.build_absolute_uri(reverse(
                    '{}-notification'.format(app),
                    kwargs={'appli': appli}
                )))
            except NoReverseMatch:
                # The library user does not have the legacy withings URLs
                pass
    if nokia_user.exists() and utils.get_setting('NOKIA_SUBSCRIBE'):
        try:
            api = utils.create_nokia(**nokia_user[0].get_user_data())
            subs = api.list_subscriptions()
            for sub in subs:
                if sub['callbackurl'] in urls:
                    api.unsubscribe(sub['callbackurl'], appli=sub['appli'])
        except:
            return redirect(reverse('nokia-error'))
    nokia_user.delete()
    next_url = request.GET.get('next', None) or utils.get_setting(
        'NOKIA_LOGOUT_REDIRECT')
    return redirect(next_url)


@csrf_exempt
def notification(request, appli):
    """ Receive notification from Nokia.

    More information here:
    https://developer.health.nokia.com/api/doc#api-Notification-Notification_callback

    URL name:
        `nokia-notification`
    """
    if request.method == 'HEAD':
        return HttpResponse()

    # The updates come in as a POST request with the necessary data
    uid = request.POST.get('userid')

    if uid and request.method == 'POST':
        for user in NokiaUser.objects.filter(nokia_user_id=uid):
            kwargs = {}
            if user.last_update:
                kwargs['lastupdate'] = user.last_update
            try:
                measures = utils.get_nokia_data(user, **kwargs)
            except Exception:
                logger.exception("Error getting nokia user measures")
            else:
                MeasureGroup.create_from_measures(user.user, measures)
                user.last_update = timezone.now()
                user.save()
        return HttpResponse(status=204)

    # If GET request or POST with bad data, raise a 404
    raise Http404
