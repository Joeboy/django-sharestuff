from django.db import models

class ThingManager(models.Manager):
    """
    Manager to make it easier to filter for live items
    """
    
    def live(self):
        """
        Return a queryset of the 'live' items (items that have been moderated and are still available)
        """
        return self.filter(live_status=True)
