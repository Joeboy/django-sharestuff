from django.conf.urls.defaults import *

urlpatterns = patterns('goingspare.oauth.views',
    url(r'^request-token$', 'request_token', name='request-token'),

    url(r'^request-token-ready', 'request_token_ready', name='request-token-ready'),
    url(r'^playpen$', 'playpen'),
)
