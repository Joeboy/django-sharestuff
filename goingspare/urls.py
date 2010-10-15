from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'goingspare.views.index', name='homepage'),
    url(r'^offers/', include('offers.urls')),
    url(r'^user/', include ('userprofile.urls')),
    url('^admin/(.*)', admin.site.root),
)

if settings.LOCAL_DEV:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )
