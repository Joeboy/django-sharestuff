from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from userprofile.models import UserProfile
import datetime
import random
import json

B36_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'
SITE_DOMAIN = Site.objects.get_current().domain

class OfferCategory(models.Model):
    title = models.CharField(max_length=255)
    parent=models.ForeignKey('self', blank=True, null=True, related_name='child')

    def __unicode__(self):
        return u'%s' % (self.title)

class LocalOfferImage(models.Model):
    image = models.ImageField(upload_to='offer_images/local')
    caption = models.TextField(blank=True, null=True)
    offer = models.ForeignKey('LocalOffer', blank=True, null=True)

class BaseOffer(models.Model):
    """
    Base class for offers
    """
#    offer_category = models.ForeignKey(OfferCategory, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time_added = models.DateTimeField(blank=True, default=datetime.datetime.now)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    class Meta:
        abstract = True
        get_latest_by = 'date_time_added'
        ordering = ['-date_time_added']
    
    def __unicode__(self):
        return u'%s' % (self.title)

class OfferManager(models.Manager):
    """
    Manager to make it easier to filter for live items
    """
    
    def live(self):
        """
        Return a queryset of the 'live' offers (offers that have been moderated and are still available)
        """
        return self.filter(live_status=True)


class LocalOffer(BaseOffer):
    """
    An offer hosted on this website
    """
    @staticmethod
    def get_random_hash():
        number = random.getrandbits(64)
        base36 = ''
        while number:
            number, i = divmod(number, 36)
            base36 = B36_ALPHABET[i] + base36
        return base36 or B36_ALPHABET[0]

    live_status = models.BooleanField("Active", default=True)
    donor = models.ForeignKey(UserProfile)
    # A slightly obfuscated id for public use:
    hash = models.CharField(max_length=25, unique=True, db_index=True, blank=True)

    objects = OfferManager()

    def get_absolute_url(self):
        return reverse('view-offer', kwargs={'offer_hash':self.hash})

    def get_full_url(self):
        return 'http://%s%s' % (SITE_DOMAIN, self.get_absolute_url())

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = self.get_random_hash()
        super(LocalOffer, self).save(*args, **kwargs)

    def image_list(self):
        """
        Convenience function for passing image info to js
        """
        return json.dumps([{'id':im.id, 'url':im.image.url, 'caption':im.caption} for im in self.localofferimage_set.order_by('id')])

class RemoteOffer(BaseOffer):
    """
    An offer hosted on another website
    """
    url = models.URLField()
