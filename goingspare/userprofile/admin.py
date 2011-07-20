from django.contrib import admin
from userprofile.models import UserProfile, Subscription

class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Subscription)

