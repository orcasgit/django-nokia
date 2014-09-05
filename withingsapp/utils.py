from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from withings import WithingsApi, WithingsAuth, WithingsCredentials

from . import defaults
from .models import WithingsUser


def create_withings(consumer_key=None, consumer_secret=None, **kwargs):
    """ Shortcut to create a WithingsApi instance. """

    consumer_key, consumer_secret = get_consumer_key_and_secret(
        consumer_key=consumer_key, consumer_secret=consumer_secret)
    creds = WithingsCredentials(consumer_key=consumer_key,
                                consumer_secret=consumer_secret, **kwargs)
    return WithingsApi(creds)


def create_withings_auth():
    consumer_key, consumer_secret = get_consumer_key_and_secret()
    return WithingsAuth(consumer_key, consumer_secret)


def get_consumer_key_and_secret(consumer_key=None, consumer_secret=None):
    """
    If consumer_key or consumer_secret are not provided, then the values
    specified in settings are used.
    """
    if consumer_key is None:
        consumer_key = get_setting('WITHINGS_CONSUMER_KEY')
    if consumer_secret is None:
        consumer_secret = get_setting('WITHINGS_CONSUMER_SECRET')

    if consumer_key is None or consumer_secret is None:
        raise ImproperlyConfigured(
            "Consumer key and consumer secret cannot be null, and must be "
            "explicitly specified or set in your Django settings")

    return (consumer_key, consumer_secret)

def is_integrated(user):
    """Returns ``True`` if we have Oauth info for the user.

    This does not require that the token and secret are valid.

    :param user: A Django User.
    """
    if user.is_authenticated() and user.is_active:
        return WithingsUser.objects.filter(user=user).exists()
    return False


def get_withings_data(withings_user, **kwargs):
    """
    Retrieves withings data for the date range
    """
    api = create_withings(**withings_user.get_user_data())
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
