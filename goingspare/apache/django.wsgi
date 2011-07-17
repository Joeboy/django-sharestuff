import os, sys
sys.path.extend(['/var/www/django/sharestuffve/sharestuff',
                 '/var/www/django/sharestuffve/sharestuff/goingspare',
                 '/var/www/django/sharestuffve/lib/python2.6/site-packages/',])

os.environ['DJANGO_SETTINGS_MODULE'] = 'goingspare.settings'
os.environ["CELERY_LOADER"] = "django"

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
