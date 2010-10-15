from django.conf.urls.defaults import *

urlpatterns = patterns('offers.views',
#    url(r'^$', 'index'),
    url(r'^my-offers/$', 'my_offers', name='my-offers'),
    url(r'^offers/$', 'others_offers', name='others-offers'),
#    url(r'^user/(?P<offer_id>\d+)/$', 'user_offers', name="user-offers"),
    url(r'^add/$', 'edit_offer', name='edit-offer'),
    url(r'^edit/(?P<offer_id>\d+)/$', 'edit_offer', name='edit-offer'),
    url(r'^delete/(?P<offer_id>\d+)/$', 'delete_offer', name='delete-offer'),
    url(r'^contact/(?P<offer_hash>[0-9a-z]{1,14})/$', 'contact_re_offer', name='contact-re-offer'),
#    url(r'^categories/$', 'offer_categories'),
#    url(r'^categories/(?P<parent_id>\d+)/$', 'offer_categories'),
#    url(r'^categories/tree/(?P<cat_id>\d+)/$', 'offer_category_tree'),
#    url(r'^search/$', 'search'),
#    url(r'^(?P<cat_slug>[\w-]+)/$', 'top_level'),
)
