#from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from django.db.models import Q
from django.core.urlresolvers import reverse

from django.conf import settings

from taggit.managers import TaggableManager

from userprofile.models import UserProfile
import datetime
import random
import json
import re

B36_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'


class OfferCategory(models.Model):
    title = models.CharField(max_length=255)
    parent=models.ForeignKey('self', blank=True, null=True, related_name='child')

    def __unicode__(self):
        return u'%s' % (self.title)

class LocalOfferImage(models.Model):
    image = models.ImageField(upload_to='offer_images/local')
    caption = models.TextField(blank=True, null=True)
    offer = models.ForeignKey('LocalOffer', blank=True, null=True)


class OfferManager(models.GeoManager):
    """
    Manager that adds the ability to create custom queryset methods, and also
    allows access to those methods by the manager itself
    """
    
    def get_query_set(self):
        return self.model.QuerySet(self.model, using=self._db)

    def __getattr__(self, attr, *args):
        if attr in ('filter_by_user',
                    'with_distances',
                    'filter_by',):
            return getattr(self.get_query_set(), attr, *args)
        else:
            return getattr(self.__class__, attr, *args)


class BaseOffer(models.Model):
    """
    Base class for offers
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time_added = models.DateTimeField(blank=True, default=datetime.datetime.now, db_index=True)
    list_public = models.BooleanField("Show listing to anybody")
    list_sharestuffers = models.BooleanField("Show listing to people logged into ShareStuff")
    list_watchers = models.BooleanField("Show listing to people watching me")
    show_public = models.BooleanField("Show details to anybody")
    show_sharestuffers = models.BooleanField("Show details to people logged into ShareStuff")
    show_watchers = models.BooleanField("Show details to people watching me")

#    latitude = models.FloatField()
#    longitude = models.FloatField()
    location = models.PointField()
    
    class Meta:
        abstract = True
        get_latest_by = 'date_time_added'
        ordering = ['-date_time_added']
    
    def __unicode__(self):
        return u'%s' % (self.title)


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
    tags = TaggableManager(blank=True)

    class QuerySet(models.query.GeoQuerySet):
        
        def filter_by_user(self, userprofile):
            """
            Filter the list down to offers the user has permission to see
            listed
            """
            q = Q(list_public=True)
            if userprofile:
                q |= Q(list_sharestuffers=True)
                q |= (Q(list_watchers=True) & Q(donor__watchers__in=[userprofile]))

            return self.filter(Q(live_status=True) & q).distinct()

        def filter_by(self, **params):
            """
            Function to grab a filtered queryset with added distance field.
            The current sql will scale abysmally and will need redoing if the site gets
            a significant number of users
            """
            (donorprofile,
             latitude,
             longitude,
             max_distance,
             watched_users,
             asking_userprofile,
             tags) = (params.get('donorprofile'),
                      params.get('latitude'),
                      params.get('longitude'),
                      params.get('max_distance'),
                      params.get('watched_users'),
                      params.get('asking_userprofile'),
                      params.get('tags'), )

            offers = LocalOffer.objects.all()

            if watched_users:
                if not asking_userprofile:
                    raise PermissionDenied("If you specify watched_users, you must also specify asking_userprofile.")
                offers = offers.filter(donor__in=asking_userprofile.watched_users.all())

            if tags:
                offers = offers.filter(tags__name__in=tags)

            if donorprofile:
                offers = offers.filter(donor=donorprofile)
            
            offers = offers.filter_by_user(asking_userprofile)

            if longitude is not None and latitude is not None:
                location = Point(longitude, latitude)

                if max_distance is not None:
                    area = (location, Distance(km=max_distance))
                    offers = LocalOffer.objects.filter(location__distance_lte=area).distance(location)
                else:
                    offers = offers.distance(location)

            return offers


    def show_to_user(self, userprofile):
        """
        Does the user have permission to view the object's details?
        """
        if not self.live_status:
            return False
        if self.show_public:
            return True
        if self.show_sharestuffers and userprofile:
            return True
        if self.show_watchers and userprofile and \
           self.donor in userprofile.watched_users.all():
            return True
        return False


    def get_absolute_url(self):
        return reverse('view-offer', kwargs={'offer_hash':self.hash})

    def get_full_url(self):
        return 'http://%s%s' % (settings.SITE_DOMAIN, self.get_absolute_url())

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = self.get_random_hash()
        super(LocalOffer, self).save(*args, **kwargs)

    def image_list(self):
        """
        Convenience function for passing image info to js
        """
        return json.dumps([{'id':im.id, 'url':im.image.url, 'caption':im.caption} for im in self.localofferimage_set.order_by('id')])

#class RemoteOffer(BaseOffer):
#    """
#    An offer hosted on another website
#    Something for the future
#    """
#    url = models.URLField()
