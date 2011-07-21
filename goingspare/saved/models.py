from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from taggit.models import Tag

class SavedFilter(models.Model):
    """
    A saved filter (/search). Ie. a user can filter offers by various criteria,
    then save their filter for later use. These will also get used for sharing
    on facebook, rss feeds and maybe other stuff.
    """
    name = models.CharField(max_length=80)
    slug = models.SlugField()

    owner = models.ForeignKey('userprofile.userprofile', related_name='saved_searches')
    donor = models.ForeignKey('userprofile.userprofile', null=True, blank=True)
    location = models.PointField(null=True, blank=True)
    max_distance = models.IntegerField(null=True, blank=True)
    watched_users = models.BooleanField()
    tags = models.ManyToManyField(Tag, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('saved-search', kwargs={'filter_slug':self.slug})
