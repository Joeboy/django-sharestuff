from django.db import models

class Outcode(models.Model):
    outcode = models.CharField(max_length=5, db_index=True)
    lat = models.FloatField()
    lng = models.FloatField()
