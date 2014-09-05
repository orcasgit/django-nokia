# Your Withings access credentials, which must be requested from Withings.
# You must provide these in your project's settings.
WITHINGS_CONSUMER_KEY = None
WITHINGS_CONSUMER_SECRET = None

# Where to redirect to after Withings authentication is successfully completed.
WITHINGS_LOGIN_REDIRECT = '/'

# Where to redirect to after Withings authentication credentials have been
# removed.
WITHINGS_LOGOUT_REDIRECT = '/'

# By default, don't subscribe to user data. Set this to true to subscribe.
WITHINGS_SUBSCRIBE = False

# The template to use when an unavoidable error occurs during Withings
# integration.
WITHINGS_ERROR_TEMPLATE = 'withings/error.html'

# The default message used by the withings_integration_warning decorator to
# inform the user about Withings integration. If a callable is given, it is
# called with the request as the only parameter to get the final value for the
# message.
WITHINGS_DECORATOR_MESSAGE = 'This page requires Withings integration.'
