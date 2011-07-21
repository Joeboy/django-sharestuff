from django.conf.urls.defaults import *

urlpatterns = patterns('saved.views',
    url(r'^save/$', 'save', name='save-search'),
    url(r'^saved/(?P<filter_slug>[0-9a-z-]+)/$', 'saved', name='saved-search'),
)

