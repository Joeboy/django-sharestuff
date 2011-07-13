from userprofile.models import UserProfile
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.contrib.syndication.views import Feed

class UserActivityFeed(Feed):
    def get_object(self, request, username):
        return get_object_or_404(UserProfile, user__username=username)

    def link(self, user):
        return user.get_absolute_url()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def items(self, obj):
        return obj.localoffer_set.all()
