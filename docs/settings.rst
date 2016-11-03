Settings
========

.. index::
    single: WITHINGS_CONSUMER_KEY

.. _WITHINGS_CONSUMER_KEY:

WITHINGS_CONSUMER_KEY
---------------------

The key assigned to your app by Withings when you register your app at
`the Withings developer site <https://account.withings.com/connectionuser/account_create>`_. You must specify a
non-null value for this setting.

.. index::
    single: WITHINGS_CONSUMER_SECRET

.. _WITHINGS_CONSUMER_SECRET:

WITHINGS_CONSUMER_SECRET
------------------------

The secret that goes with the WITHINGS_CONSUMER_KEY. You must specify a non-null
value for this setting.

.. _WITHINGS_LOGIN_REDIRECT:

WITHINGS_LOGIN_REDIRECT
-----------------------

:Default:  ``'/'``

The URL which to redirect the user to after successful Withings integration, if
no forwarding URL is given in the 'withings_next' session variable.

.. _WITHINGS_LOGOUT_REDIRECT:

WITHINGS_LOGOUT_REDIRECT
------------------------

:Default: ``'/'``

The URL which to redirect the user to after removal of Withings account
credentials, if no forwarding URL is given in the 'next' GET parameter.

.. _WITHINGS_SUBSCRIBE:

WITHINGS_SUBSCRIBE
------------------

:Default: ``False``

When this setting is True, we will subscribe to user data (currently just
weight, blood pressure, and heart rate). Withings will send notifications when
the data changes and we will make an immediate API call to retrieve the data
and store it locally.

.. _WITHINGS_ERROR_TEMPLATE:

WITHINGS_ERROR_TEMPLATE
-----------------------

:Default:  ``'withings/error.html'``

The template used to report an error integrating the user's Withings.

.. _WITHINGS_DECORATOR_MESSAGE:

WITHINGS_DECORATOR_MESSAGE
--------------------------

:Default: ``'This page requires Withings integration.'``

The default message used by the
:py:func:`withingsapp.decorators.withings_integration_warning` decorator to inform
the user about Withings integration. If a callable is provided, it is called
with the request as the only parameter to get the final value for the message.
