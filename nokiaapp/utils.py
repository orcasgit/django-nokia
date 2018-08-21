from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from nokia import NokiaApi, NokiaAuth, NokiaCredentials

from . import defaults
from .models import NokiaUser


def create_nokia(client_id=None, consumer_secret=None, **kwargs):
    """ Shortcut to create a NokiaApi instance. """

    refresh_cb = kwargs.pop('refresh_cb', None)
    return NokiaApi(get_creds(
        client_id=client_id,
        consumer_secret=consumer_secret,
        **kwargs
    ), refresh_cb=refresh_cb)


def create_nokia_auth(callback_uri):
    creds = get_creds()

    return NokiaAuth(creds.client_id, creds.consumer_secret, callback_uri)


def get_creds(client_id=None, consumer_secret=None, **kwargs):
    """
    If client_id or consumer_secret are not provided, then the values specified
    in settings are used.
    """
    if client_id is None:
        client_id = get_setting('NOKIA_CLIENT_ID')
    if consumer_secret is None:
        consumer_secret = get_setting('NOKIA_CONSUMER_SECRET')

    if not all([client_id, consumer_secret]):
        raise ImproperlyConfigured(
            "Neither lient id nor consumer secret can be null, they must be "
            "explicitly specified or set in your Django settings")

    return NokiaCredentials(
        client_id=client_id, consumer_secret=consumer_secret, **kwargs)


def is_integrated(user):
    """Returns ``True`` if we have Oauth info for the user.

    This does not require that the token and secret are valid.

    :param user: A Django User.
    """
    if user.is_authenticated() and user.is_active:
        return NokiaUser.objects.filter(user=user).exists()
    return False


def get_nokia_data(nokia_user, **kwargs):
    """
    Retrieves nokia data for the date range
    """
    api = create_nokia(**nokia_user.get_user_data())
    return api.get_measures(**kwargs)


def get_setting(name, use_defaults=True):
    """Retrieves the specified setting from the settings file.

    If the setting is not found and use_defaults is True, then the default
    value specified in defaults.py is used. Otherwise, we raise an
    ImproperlyConfigured exception for the setting.
    """
    if hasattr(settings, name):
        return getattr(settings, name)
    if use_defaults:
        if hasattr(defaults, name):
            return getattr(defaults, name)
    msg = "{0} must be specified in your settings".format(name)
    raise ImproperlyConfigured(msg)
