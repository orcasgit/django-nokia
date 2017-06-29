Migrate from django-withings
============================

When migrating django-withings to django-nokia, there are a couple extra steps
you need to take to keep things running smoothly.

1. Uninstall `django-withings` and install `django-nokia`

2. Add `nokiaapp` to your INSTALLED_APPS setting and remove `withingsapp`

3. Adjust your URLconf to retain the old withings routes, while adding nokia
   routes. This makes sure you can continue receiving notifications of old
   subscriptions. Make sure the ``nokia/`` route is second so that URL
   reversals resolve to it. If you don't have old subscriptions, you may not
   need the old ``withings/`` routes::

    url(r'^withings/', include('nokiaapp.urls')),
    url(r'^nokia/', include('nokiaapp.urls')),

4. Adjust all ``WITHINGS_<SETTING>`` settings to ``NOKIA_<SETTING>``

5. Run ``./manage.py migrate nokiaapp --fake-initial`` to migrate all your
   existing data to the new models. This is a one time thing. For future
   migrations, you can just run ``./manage.py migrate``
