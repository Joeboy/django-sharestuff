from django.conf.urls.defaults import *

urlpatterns = patterns('goingspare.notifications.views',
    url(r'^$', 'index', name='notifications'),
)
