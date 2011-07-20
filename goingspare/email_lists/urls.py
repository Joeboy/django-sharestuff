from django.conf.urls.defaults import *

urlpatterns = patterns('email_lists.views',
#    url(r'^$', 'index'),
    url(r'^add-subscription/$', 'add_subscription', name='add-subscription'),
    url(r'^get-message/(?P<subscription_id>\d+)/(?P<offer_hash>[0-9a-z]+)/$', 'get_message', name='get_emaillist_message'),
)
