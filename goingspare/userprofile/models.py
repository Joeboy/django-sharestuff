from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from utils.dbfields import UKPhoneNumberField
     
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    phone_number = UKPhoneNumberField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    email_contact = models.BooleanField("Email me when people contact me about my offers", default=True)

    notify_following = models.BooleanField("Notify me when somebody asks to follow me", default=True)
    confirm_following = models.BooleanField("Ask me for permission before allowing people to follow me")

    public_offers = models.BooleanField("List my offers publicly by default")

    watched_users = models.ManyToManyField('UserProfile', blank=True)

    def get_best_name(self):
        return self.name or self.user.username

    def __unicode__(self):
        return "%s's UserProfile" % self.user.username

    def get_absolute_url(self):
        return reverse('view-userprofile', kwargs={'user_id':self.id})
