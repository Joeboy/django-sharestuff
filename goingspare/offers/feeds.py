from userprofile.models import UserProfile
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.contrib.syndication.views import Feed

class UserActivityFeed(Feed):
    feed_type = Atom1Feed
    def get_object(self, request, user_id):
        return get_object_or_404(UserProfile, id=user_id)

    def link(self, user):
        return user.get_absolute_url()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def items(self, obj):
        return obj.localoffer_set.all()
