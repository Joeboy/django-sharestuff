from django.contrib import admin
from email_lists.models import EmailMessage, EmailList

admin.site.register(EmailList)
admin.site.register(EmailMessage)
