from django.db import models
from userprofile.models import UserProfile
from offers.managers import OfferManager
import datetime

class Offer(models.Model):
    "An item of stuff to get rid of"
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time_added = models.DateTimeField(blank=True, default=datetime.datetime.now)
    live_status = models.BooleanField(default=True)
    regular = models.BooleanField(default=False)

    # Have the donor / other user reported it taken?
    taken_status_donor = models.BooleanField(default=False)
    taken_status_other = models.BooleanField(default=False)

    donor = models.ForeignKey(UserProfile)
    
    # Managers
    objects = OfferManager()
    
    class Meta:
        get_latest_by = 'date_time_added'
        ordering = ['-date_time_added']
    
    class Admin:
        date_hierarchy = 'date_time_added'
        list_display = ('title', 'live_status', 'taken_status_donor')

    def __unicode__(self):
        return u'%s' % (self.title)

class OfferImage(models.Model):
    caption = models.CharField(max_length=100)
    image = models.ImageField(upload_to="offers/")
    offer = models.ForeignKey(Offer)

    def __unicode__(self):
        return self.caption

    class Meta:
        pass

    class Admin:
        pass
