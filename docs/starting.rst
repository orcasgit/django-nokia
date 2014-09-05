Getting started
===============

.. index::
    single: PyPI

1. Add `django-withings` to your Django site's requirements, however you prefer,
   and install it.  It's installable from `PyPI
   <http://pypi.python.org/pypi/django-withings/>`_.

.. index::
    single: INSTALLED_APPS

2. Add `withingsapp` to your INSTALLED_APPS setting::

    INSTALLED_APPS += ['withingsapp']

3. Add the `django-withings` URLs to your URLconf::

    url(r'^withings/', include('withingsapp.urls')),

3. Register your site at the `Withings developer site <http://oauth.withings.com/partner/dashboard>`_
   to get a key and secret.

4. Add settings for :ref:`WITHINGS_CONSUMER_KEY` and
   :ref:`WITHINGS_CONSUMER_SECRET`::

    WITHINGS_CONSUMER_KEY = 'abcdefg123456'
    WITHINGS_CONSUMER_SECRET = 'abcdefg123456'

5. If you need to change the defaults, add settings for
   :ref:`WITHINGS_LOGIN_REDIRECT`, :ref:`WITHINGS_LOGOUT_REDIRECT`, and/or
   :ref:`WITHINGS_ERROR_TEMPLATE`.

6. To display whether the user has integrated their Withings, or change a
   template behavior, use the :ref:`is_integrated_with_withings` template
   filter. Or in a view, call the :py:func:`withingsapp.utils.is_integrated`
   function. You can also use the decorator
   :py:func:`withingsapp.decorators.withings_integration_warning` to display a message to the
   user when they are not integrated with Withings.

7. To send the user through authorization at the Withings site for your app to
   access their data, send them to the :py:func:`withingsapp.views.login` view.
