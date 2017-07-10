# Your Nokia access credentials, which must be requested from Nokia.
# You must provide these in your project's settings.
NOKIA_CONSUMER_KEY = None
NOKIA_CONSUMER_SECRET = None

# Where to redirect to after Nokia authentication is successfully completed.
NOKIA_LOGIN_REDIRECT = '/'

# Where to redirect to after Nokia authentication credentials have been
# removed.
NOKIA_LOGOUT_REDIRECT = '/'

# By default, don't subscribe to user data. Set this to true to subscribe.
NOKIA_SUBSCRIBE = False

# The template to use when an unavoidable error occurs during Nokia
# integration.
NOKIA_ERROR_TEMPLATE = 'nokia/error.html'

# The default message used by the nokia_integration_warning decorator to
# inform the user about Nokia integration. If a callable is given, it is
# called with the request as the only parameter to get the final value for the
# message.
NOKIA_DECORATOR_MESSAGE = 'This page requires Nokia integration.'
