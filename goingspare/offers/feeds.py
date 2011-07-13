from userprofile.models import UserProfile
from django.shortcuts import get_object_or_404
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse

class UserActivityFeed(Feed):
    def get_object(self, request, username):
        return get_object_or_404(UserProfile, user__username=username)

    def link(self, userprofile):
        return reverse('user-offers', kwargs={'username':userprofile.user.username})

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def items(self, obj):
        return obj.localoffer_set.all()
