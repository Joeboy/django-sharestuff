from django.conf.urls.defaults import *

urlpatterns = patterns('email_lists.views',
#    url(r'^$', 'index'),
    url(r'^add-subscription/$', 'add_subscription', name='add-subscription'),
)
