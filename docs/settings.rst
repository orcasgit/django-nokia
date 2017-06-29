Settings
========

.. index::
    single: NOKIA_CONSUMER_KEY

.. _NOKIA_CONSUMER_KEY:

NOKIA_CONSUMER_KEY
---------------------

The key assigned to your app by Nokia when you register your app at
`the Nokia developer site <https://developer.health.nokia.com/en/partner/add>`_. You must specify a
non-null value for this setting.

.. index::
    single: NOKIA_CONSUMER_SECRET

.. _NOKIA_CONSUMER_SECRET:

NOKIA_CONSUMER_SECRET
------------------------

The secret that goes with the NOKIA_CONSUMER_KEY. You must specify a non-null
value for this setting.

.. _NOKIA_LOGIN_REDIRECT:

NOKIA_LOGIN_REDIRECT
-----------------------

:Default:  ``'/'``

The URL which to redirect the user to after successful Nokia integration, if
no forwarding URL is given in the 'nokia_next' session variable.

.. _NOKIA_LOGOUT_REDIRECT:

NOKIA_LOGOUT_REDIRECT
------------------------

:Default: ``'/'``

The URL which to redirect the user to after removal of Nokia account
credentials, if no forwarding URL is given in the 'next' GET parameter.

.. _NOKIA_SUBSCRIBE:

NOKIA_SUBSCRIBE
------------------

:Default: ``False``

When this setting is True, we will subscribe to user data (currently just
weight, blood pressure, and heart rate). Nokia will send notifications when
the data changes and we will make an immediate API call to retrieve the data
and store it locally.

.. _NOKIA_ERROR_TEMPLATE:

NOKIA_ERROR_TEMPLATE
-----------------------

:Default:  ``'nokia/error.html'``

The template used to report an error integrating the user's Nokia.

.. _NOKIA_DECORATOR_MESSAGE:

NOKIA_DECORATOR_MESSAGE
--------------------------

:Default: ``'This page requires Nokia integration.'``

The default message used by the
:py:func:`nokiaapp.decorators.nokia_integration_warning` decorator to inform
the user about Nokia integration. If a callable is provided, it is called
with the request as the only parameter to get the final value for the message.
