from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'userprofile.views.index'),
    url(r'^(?P<user_id>\d+)/$', 'userprofile.views.view_profile', name="view-userprofile"),
    url(r'^edit/$', 'userprofile.views.edit', name='edit-userprofile'),
    url(r'^updated/$', 'userprofile.views.updated'),
    url(r'^change-password/$', 'userprofile.views.change_password'),
    url(r'^password-changed/$', 'userprofile.views.password_changed'),
    url(r'^list/$', 'userprofile.views.user_list', name="user-list"),
    url(r'^watch/(?P<user_id>\d+)/$', 'userprofile.views.watch_user', name="watch-user"),
    url(r'^unwatch/(?P<user_id>\d+)/$', 'userprofile.views.watch_user', {'unwatch':True}, name="unwatch-user"),
#    url(r'register/$', 'registration.views.register'),#, {'profile_callback':create_userprofile}),
    url(r'', include('registration.urls')),

#    url(r'^manage/$', 'userprofile.views.manage_users'),
#    url(r'^manage/add/$', 'userprofile.views.edit_user'),
#    url(r'^manage/edit/(?P<id>\d+)/$', 'userprofile.views.edit_user', name="manage_userprofile"),
#    url(r'^manage/delete/(?P<id>\d+)/$', 'userprofile.views.delete_user', name="delete_userprofile"),
)

