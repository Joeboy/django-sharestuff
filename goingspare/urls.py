from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'goingspare.views.index', name='homepage'),
    url(r'^offers/', include('offers.urls')),
    url(r'^saved/', include('saved.urls')),
    url(r'^user/', include ('userprofile.urls')),
    url(r'^email-lists/', include('email_lists.urls')),
    url(r'^notifications/', include('notifications.urls')),
    url(r'^oauth/', include('oauth.urls')),
    url('^admin/', admin.site.urls),
    url(r'^sentry/', include('sentry.web.urls')),

)

if settings.LOCAL_DEV:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )
