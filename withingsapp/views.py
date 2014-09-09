import json

from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import utils
from .models import WithingsUser, MeasureGroup


@login_required
def login(request):
    """
    Begins the OAuth authentication process by obtaining a Request Token from
    Withings and redirecting the user to the Withings site for authorization.

    When the user has finished at the Withings site, they will be redirected
    to the :py:func:`withingsapp.views.complete` view.

    If 'next' is provided in the GET data, it is saved in the session so the
    :py:func:`withingsapp.views.complete` view can redirect the user to that
    URL upon successful authentication.

    URL name:
        `withings-login`
    """
    next_url = request.GET.get('next', None)
    if next_url:
        request.session['withings_next'] = next_url
    else:
        request.session.pop('withings_next', None)

    callback_uri = request.build_absolute_uri(reverse('withings-complete'))
    auth = utils.create_withings_auth()
    auth_url = auth.get_authorize_url(callback_uri=callback_uri)
    request.session['oauth_token'] = auth.oauth_token
    request.session['oauth_secret'] = auth.oauth_secret
    return redirect(auth_url)


@login_required
def complete(request):
    """
    After the user authorizes us, Withings sends a callback to this URL to
    complete authentication.

    If there was an error, the user is redirected again to the `error` view.

    If the authorization was successful, the credentials are stored for us to
    use later, and the user is redirected. If 'next_url' is in the request
    session, the user is redirected to that URL. Otherwise, they are
    redirected to the URL specified by the setting
    :ref:`WITHINGS_LOGIN_REDIRECT`.

    If :ref:`WITHINGS_SUBSCRIBE` is set to True, add a subscription to user
    data at this time.

    URL name:
        `withings-complete`
    """
    auth = utils.create_withings_auth()
    try:
        auth.oauth_token = request.session.pop('oauth_token')
        auth.oauth_secret = request.session.pop('oauth_secret')
        verifier = request.GET.get('oauth_verifier')
        user_id = request.GET.get('userid')
    except KeyError:
        return redirect(reverse('withings-error'))
    if not verifier or not user_id:
        return redirect(reverse('withings-error'))
    try:
        creds = auth.get_credentials(verifier)
    except:
        return redirect(reverse('withings-error'))


    user_updates = {'access_token': creds.access_token,
                    'access_token_secret': creds.access_token_secret,
                    'withings_user_id': user_id}
    withings_user = WithingsUser.objects.filter(user=request.user)
    if withings_user.exists():
        withings_user.update(**user_updates)
        withings_user = withings_user[0]
    else:
        user_updates['user'] = request.user
        withings_user = WithingsUser.objects.create(**user_updates)
    # Add the Withings user info to the session
    api = utils.create_withings(**withings_user.get_user_data())
    request.session['withings_profile'] = api.get_user()
    MeasureGroup.create_from_measures(request.user, api.get_measures())
    request.user.last_update = timezone.now()
    request.user.save()
    if utils.get_setting('WITHINGS_SUBSCRIBE'):
        for appli in [1, 4]:
            notification_url = request.build_absolute_uri(
                reverse('withings-notification', kwargs={'appli': appli}))
            api.subscribe(notification_url, 'django-withings', appli=appli)

    next_url = request.session.pop('withings_next', None) or utils.get_setting(
        'WITHINGS_LOGIN_REDIRECT')
    return redirect(next_url)


@receiver(user_logged_in)
def create_withings_session(sender, request, user, **kwargs):
    """ If the user is a Withings user, update the profile in the session. """

    if (user.is_authenticated() and utils.is_integrated(user) and
            user.is_active):
        withings_user = WithingsUser.objects.filter(user=user)
        if withings_user.exists():
            api = utils.create_withings(**withings_user[0].get_user_data())
            try:
                request.session['withings_profile'] = api.get_user()
            except:
                pass


@login_required
def error(request):
    """
    The user is redirected to this view if we encounter an error acquiring
    their Withings credentials. It renders the template defined in the setting
    :ref:`WITHINGS_ERROR_TEMPLATE`. The default template, located at
    *withings/error.html*, simply informs the user of the error::

        <html>
            <head>
                <title>Withings Authentication Error</title>
            </head>
            <body>
                <h1>Withings Authentication Error</h1>

                <p>We encontered an error while attempting to authenticate you
                through Withings.</p>
            </body>
        </html>

    URL name:
        `withings-error`
    """
    return render(request, utils.get_setting('WITHINGS_ERROR_TEMPLATE'), {})


@login_required
def logout(request):
    """Forget this user's Withings credentials.

    If the request has a `next` parameter, the user is redirected to that URL.
    Otherwise, they're redirected to the URL defined in the setting
    :ref:`WITHINGS_LOGOUT_REDIRECT`.

    URL name:
        `withings-logout`
    """
    withings_user = WithingsUser.objects.filter(user=request.user)
    if withings_user.exists() and utils.get_setting('WITHINGS_SUBSCRIBE'):
        try:
            api = utils.create_withings(**withings_user[0].get_user_data())
            for appli in [1, 4]:
                notification_url = request.build_absolute_uri(
                    reverse('withings-notification', kwargs={'appli': appli}))
                subs = api.list_subscriptions(appli=appli)
                if len(subs) > 0:
                    api.unsubscribe(notification_url, appli=appli)
        except:
            return redirect(reverse('withings-error'))
    withings_user.delete()
    next_url = request.GET.get('next', None) or utils.get_setting(
        'WITHINGS_LOGOUT_REDIRECT')
    return redirect(next_url)


@csrf_exempt
@require_POST
def notification(request, appli):
    """ Receive notification from Withings.

    Create celery tasks to get the data. More information here:
    http://oauth.withings.com/api/doc#api-Notification-Notification_callback

    URL name:
        `withings-notification`
    """

    # The updates come in as a POST request with the necessary data
    uid = request.POST.get('userid')

    if uid and request.POST.get('startdate') and request.POST.get('enddate'):
        for user in WithingsUser.objects.filter(withings_user_id=uid):
            kwargs = {}
            if user.last_update:
                kwargs['lastupdate'] = user.last_update
            measures = utils.get_withings_data(user, **kwargs)
            MeasureGroup.create_from_measures(user.user, measures)
            user.last_update = timezone.now()
            user.save()
        return HttpResponse(status=204)

    # if someone enters the url into the browser, raise a 404
    raise Http404
