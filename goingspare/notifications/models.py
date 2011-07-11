from django.db import models

class NotificationManager(models.Manager):
    def unread(self):
        return self.get_query_set().filter(read=False)

class Notification(models.Model):
    message = models.TextField()
    to_user = models.ForeignKey('userprofile.UserProfile')
    read = models.BooleanField(default=False)

    objects = NotificationManager()

    def __unicode__(self):
        return "Notification: %s" % (self.message,)
