from django.db import models

class EmailList(models.Model):
    """
    A 'freecycle' type group
    """
    email = models.EmailField()
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s <%s>" % (self.name, self.email)
