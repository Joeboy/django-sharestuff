from django.db import models
from datetime import datetime
from django.core.mail import send_mail

MESSAGE_TYPES = ( 'OFFER', 'TAKEN', 'WANTED', 'RECEIVED',)
MESSAGE_TYPE_CHOICES = [(k, k) for k in MESSAGE_TYPES]

class EmailMessage(models.Model):
    """
    An email message, send by a user to an email list the user is subscribed
    to.
    """
    subscription = models.ForeignKey('userprofile.subscription')
    offer = models.ForeignKey('offers.LocalOffer')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    subject = models.TextField()
    body = models.TextField()
    datetime_sent = models.DateTimeField(blank=True, null=True)

    def send_mail(self, *args, **kwargs):
        send_mail(self.subject,
                  self.body,
                  self.subscription.from_email,
                  [self.subscription.email_list.email],
                  fail_silently=False)
        self.datetime_sent = datetime.now()
        self.save(*args, **kwargs)


class EmailList(models.Model):
    """
    A 'freecycle' type group
    """
    email = models.EmailField()
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s <%s>" % (self.name, self.email)
