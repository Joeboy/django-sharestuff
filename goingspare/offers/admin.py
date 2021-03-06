from django.contrib import admin
from offers.models import LocalOffer, OfferCategory, LocalOfferImage

class LocalOfferAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_time_added'
    list_display = ('title', 'live_status')

class OfferCategoryAdmin(admin.ModelAdmin):
    pass

class LocalOfferImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(LocalOffer, LocalOfferAdmin)
admin.site.register(OfferCategory, OfferCategoryAdmin)
admin.site.register(LocalOfferImage, LocalOfferImageAdmin)

