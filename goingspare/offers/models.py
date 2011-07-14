from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from taggit.managers import TaggableManager

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
    list_public = models.BooleanField("Show listing to anybody")
    list_sharestuffers = models.BooleanField("Show listing to people logged into ShareStuff")
    list_watchers = models.BooleanField("Show listing to people watching me")
    show_public = models.BooleanField("Show details to anybody")
    show_sharestuffers = models.BooleanField("Show details to people logged into ShareStuff")
    show_watchers = models.BooleanField("Show details to people watching me")

    latitude = models.FloatField()
    longitude = models.FloatField()
    
    class Meta:
        abstract = True
        get_latest_by = 'date_time_added'
        ordering = ['-date_time_added']
    
    def __unicode__(self):
        return u'%s' % (self.title)

class OfferManager(models.Manager):
    """
    Manager that adds the ability to create custom queryset methods, and also
    allows access to those methods by the manager itself
    """
    
    def get_query_set(self):
        return self.model.QuerySet(self.model)

    def list_for_user(self, userprofile):
        return self.get_query_set().list_for_user(userprofile)
        
    def with_distances(self, longitude, latitude):
        return self.get_query_set().with_distances(longitude, latitude)
        
    

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
    tags = TaggableManager()

    class QuerySet(models.query.QuerySet):
        def with_distances(self, latitude, longitude):
            """
            Add distances to the query results using pg's earth_distance function
            """
            return self.extra(select={'distance':'earth_distance(ll_to_earth(%s,%s), ll_to_earth(offers_localoffer.latitude, offers_localoffer.longitude))/1000'}, select_params=(latitude, longitude))
        
        def list_for_user(self, userprofile):
            """
            Filter the list down to offers the user has permission to see
            listed
            """
            q = Q(list_public=True)
            if userprofile:
                q |= Q(list_sharestuffers=True)
                q |= (Q(list_watchers=True) & Q(donor__watchers__in=[userprofile]))

            return self.filter(Q(live_status=True) & q)


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
    Something for the future
    """
    url = models.URLField()
