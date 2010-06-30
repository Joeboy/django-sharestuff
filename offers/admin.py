from django.contrib import admin
from offers.models import Offer, OfferImage

class OfferAdmin(admin.ModelAdmin):
    pass

class OfferImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferImage, OfferImageAdmin)
