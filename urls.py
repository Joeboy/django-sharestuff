from django.conf.urls.defaults import *
from settings import DEV_SERVER, MEDIA_ROOT
from userprofile.models import create_userprofile

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'sharestuff.views.home'),

#    (r'^stuff/', include('things.urls')),
    (r'^accounts/profile/$', 'django.views.generic.simple.redirect_to', {'url':'/userprofile/',}),
    (r'^accounts/register/$', 'registration.views.register', {'profile_callback':create_userprofile,}),
    (r'^accounts/', include('registration.urls')),
    (r'^userprofile/', include ('userprofile.urls')),
    (r'^~(?P<username>\w+)/', 'things.views.user_stuff_list'),

    (r'^admin/', include(admin.site.urls)),
)


if DEV_SERVER:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': MEDIA_ROOT,
                                   'show_indexes': True}),
    )

