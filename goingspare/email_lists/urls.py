from django.conf.urls.defaults import *

urlpatterns = patterns('email_lists.views',
#    url(r'^$', 'index'),
    url(r'^add-email-list/$', 'add_email_list', name='add-email-list'),
)
