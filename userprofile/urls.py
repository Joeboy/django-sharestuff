from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'userprofile.views.home', name="user_home"),
    url(r'^my-offers/$', 'userprofile.views.my_offers', name="my_offers"),
    url(r'^add-offer/$', 'userprofile.views.edit_offer', name="add_offer"),
    url(r'^edit-offer/(?P<offer_id>[\d+])/$', 'userprofile.views.edit_offer', name="edit_offer"),
    url(r'^delete-offer/(?P<offer_id>[\d+])/$', 'userprofile.views.delete_offer', name="delete_offer"),
)

