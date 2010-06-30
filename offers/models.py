from django.db import models
from django.conf import settings

import datetime

from sorethumb.filters.defaultfilters import *
from sorethumb.filters.drawfilters import *
from sorethumb.djangothumbnail import DjangoThumbnail

from userprofile.models import UserProfile
from offers.managers import OfferManager

import os

class Offer(models.Model):
    """
    An item of stuff to get rid of
    """
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time_added = models.DateTimeField(blank=True, default=datetime.datetime.now)
    live_status = models.BooleanField(default=True)
    regular = models.BooleanField(default=False)

    # Have the donor / other user reported it taken?
    taken_status_donor = models.BooleanField(default=False)
    taken_status_other = models.BooleanField(default=False)

    donor = models.ForeignKey(UserProfile)
    
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
    """
    A picture associated with an Offer
    """
    caption = models.CharField(max_length=100)
    image = models.ImageField(upload_to="offers/")
    offer = models.ForeignKey(Offer)
    thumbnail = models.ImageField(upload_to="offers/thumbs/",
                                  null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Update render the thumbnail field from the image field
        """
        super(OfferImage, self).save(*args, **kwargs)
        self.thumbnail = DjangoThumbnail.render("thumbnail_image", self.image.path)[7:]
        super(OfferImage, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.caption


class RoundedCornersThumbnail(DjangoThumbnail):
    """
    Thumbnail declaration for Offer thumbnails
    """
    name = 'thumbnail_image'
    format = 'png'
    filters = [SquareFilter(),
               ThumbnailFilter(90, 90),
               RoundedCornerFilter(7, border='#333'),]

    class Settings:
        """
        Sneakily put thumbnails under the thumbnail field's upload_to dir
        """
        thumbnail_field = OfferImage._meta.get_field_by_name('thumbnail')[0]
        _upload_to = thumbnail_field.upload_to
        SORETHUMB_OUTPUT_PATH = os.path.join(settings.MEDIA_ROOT,
                                             os.path.normpath(_upload_to))
        SORETHUMB_URL_ROOT = '%s%s' % (settings.MEDIA_URL, _upload_to)
        SORETHUMB_IMAGE_ROOT = settings.MEDIA_ROOT

