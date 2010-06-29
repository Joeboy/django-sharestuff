from django.contrib import admin
from things.models import Thing, ThingImage

class ThingAdmin(admin.ModelAdmin):
    pass

class ThingImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Thing, ThingAdmin)
admin.site.register(ThingImage, ThingImageAdmin)
