Getting started
===============

.. index::
    single: PyPI

1. Add `django-nokia` to your Django site's requirements, however you prefer,
   and install it.  It's installable from `PyPI
   <http://pypi.python.org/pypi/django-nokia/>`_.

.. index::
    single: INSTALLED_APPS

2. Add `nokiaapp` to your INSTALLED_APPS setting::

    INSTALLED_APPS += ['nokiaapp']

3. Add the `django-nokia` URLs to your URLconf::

    url(r'^nokia/', include('nokiaapp.urls')),

3. Register your site at the `Nokia developer site <https://developer.health.nokia.com/en/partner/add>`_
   to get a key and secret.

4. Add settings for :ref:`NOKIA_CONSUMER_KEY` and
   :ref:`NOKIA_CONSUMER_SECRET`::

    NOKIA_CONSUMER_KEY = 'abcdefg123456'
    NOKIA_CONSUMER_SECRET = 'abcdefg123456'

5. If you need to change the defaults, add settings for
   :ref:`NOKIA_LOGIN_REDIRECT`, :ref:`NOKIA_LOGOUT_REDIRECT`, and/or
   :ref:`NOKIA_ERROR_TEMPLATE`.

6. To display whether the user has integrated their Nokia, or change a
   template behavior, use the :ref:`is_integrated_with_nokia` template
   filter. Or in a view, call the :py:func:`nokiaapp.utils.is_integrated`
   function. You can also use the decorator
   :py:func:`nokiaapp.decorators.nokia_integration_warning` to display a message to the
   user when they are not integrated with Nokia.

7. To send the user through authorization at the Nokia site for your app to
   access their data, send them to the :py:func:`nokiaapp.views.login` view.
