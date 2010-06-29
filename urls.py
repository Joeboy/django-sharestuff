from django.conf.urls.defaults import *
from settings import DEV_SERVER, MEDIA_ROOT
from userprofile.models import create_userprofile

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'sharestuff.views.home', name="website_home"),

    url(r'^accounts/profile/$', 'django.views.generic.simple.redirect_to', {'url':'/userprofile/',}),
    url(r'^accounts/register/$', 'registration.views.register', {'profile_callback':create_userprofile,}),
    url(r'^accounts/', include('registration.urls')),

    url(r'^userprofile/', include ('userprofile.urls')),

    url(r'^~(?P<username>\w+)/$', 'userprofile.views.user_details', name="user_details"),
    url(r'^~(?P<username>\w+)/offers/$', 'things.views.user_offer_list', name="user_offer_list"),

    (r'^admin/', include(admin.site.urls)),
)


if DEV_SERVER:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                                  {'document_root': MEDIA_ROOT,
                                   'show_indexes': True}),
    )

