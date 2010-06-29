from django.db import models
from django.contrib.auth.models import User
     
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    easting = models.FloatField(blank=True, null=True)
    northing = models.FloatField(blank=True, null=True)
    commercial = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s's UserProfile" % self.user.username

    def live_items_count(self):
        return self.item_set.filter(live_status=True).count()

    class Meta:
        pass

    class Admin:
        pass

def create_userprofile(user):
    """Callback to pass to account registration view"""
    userprofile = UserProfile.objects.create(user=user)
    userprofile.save()
    return

