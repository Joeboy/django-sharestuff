from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

from utils.dbfields import UKPhoneNumberField, UKPostcodeField

#EMAIL_LISTS = (('norwichfreegle@yahoogroups.com', 'Norwich Freegle'),
#               ('norwichukfreecycle@groups.freecycle.org', 'Norwich Freecycle')
#)


class Subscription(models.Model):
    email_list = models.ForeignKey('email_lists.EmailList')
    userprofile = models.ForeignKey('userprofile.UserProfile')
    from_email = models.EmailField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.email_list)
     

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    phone_number = UKPhoneNumberField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    postcode = UKPostcodeField(null=True, blank=True)
#    latitude = models.FloatField(blank=True, null=True)
#    longitude = models.FloatField(blank=True, null=True)
    location = models.PointField(blank=True, null=True)

    email_contact = models.BooleanField("Email me when people contact me about my offers", default=True)

    notify_following = models.BooleanField("Notify me when somebody asks to follow me", default=True)
    confirm_following = models.BooleanField("Ask me for permission before allowing people to follow me")

    offers_list_public = models.BooleanField("Show my offers' listings to anybody", default=True)
    offers_list_sharestuffers = models.BooleanField("Show my offers' listings to people logged into FreeShop", default=True)
    offers_list_watchers = models.BooleanField("Show my offers' listings to people watching me", default=True)

    offers_show_public = models.BooleanField("Show my offers' details to anybody")
    offers_show_sharestuffers = models.BooleanField("Show my offers' details to people logged into FreeShop", default=True)
    offers_show_watchers = models.BooleanField("Show my offers' details to people watching me", default=True)
    

    watched_users = models.ManyToManyField('UserProfile', blank=True, related_name="watchers")

    email_lists = models.ManyToManyField('email_lists.EmailList', through=Subscription, blank=True)

    def get_best_name(self):
        return self.name or self.user.username

    def get_vague_area(self):
        return self.postcode and self.postcode.split(' ')[0] or 'Where?'

    def __unicode__(self):
        return "%s's UserProfile" % self.user.username

    def get_absolute_url(self):
        return reverse('user-offers', kwargs={'username':self.user.username})

    @staticmethod
    def get_for_user(user):
        if user.is_authenticated():
            return user.get_profile()
        else:
            return None
