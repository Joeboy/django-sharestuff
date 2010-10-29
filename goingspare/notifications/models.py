from django.db import models

class Notification(models.Model):
    message = models.TextField()
    to_user = models.ForeignKey('userprofile.UserProfile')

    def __unicode__(self):
        return "Notification: %s" % (self.message,)
