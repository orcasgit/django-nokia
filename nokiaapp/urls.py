from django.conf.urls import url

from . import views


urlpatterns = [
    # OAuth authentication
    url(r'^login/$', views.login, name='nokia-login'),
    url(r'^complete/$', views.complete, name='nokia-complete'),
    url(r'^error/$', views.error, name='nokia-error'),
    url(r'^logout/$', views.logout, name='nokia-logout'),

    # Subscriber callback for notifications
    url(r'^notification/(?P<appli>[14])/$', views.notification,
        name='nokia-notification')
]
