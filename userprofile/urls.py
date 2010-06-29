from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'userprofile.views.home'),
    (r'^my-stuff/$', 'userprofile.views.my_stuff'),
    (r'^add-stuff/$', 'userprofile.views.edit_thing'),
    (r'^edit-stuff/(?P<thing_id>[\d+])/$', 'userprofile.views.edit_thing'),
    (r'^delete-stuff/(?P<thing_id>[\d+])/$', 'userprofile.views.delete_thing'),
)

