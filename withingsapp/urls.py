from django.conf.urls import url

from . import views


urlpatterns = [
    # OAuth authentication
    url(r'^login/$', views.login, name='withings-login'),
    url(r'^complete/$', views.complete, name='withings-complete'),
    url(r'^error/$', views.error, name='withings-error'),
    url(r'^logout/$', views.logout, name='withings-logout'),

    # Subscriber callback for notifications
    url(r'^notification/(?P<appli>[14])/$', views.notification,
        name='withings-notification')
]
