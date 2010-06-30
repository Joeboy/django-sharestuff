from django.db import models

class OfferManager(models.Manager):
    """
    Manager to make it easier to filter for live items
    """
    
    def live(self):
        """
        Return a queryset of the 'live' offers (offers that have been moderated and are still available)
        """
        return self.filter(live_status=True)
