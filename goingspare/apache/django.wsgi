import os, sys
sys.path.extend(['/var/www/django', '/var/www/django/goingspare', '/usr/local/lib/python2.5/django/1.1/',])

os.environ['DJANGO_SETTINGS_MODULE'] = 'goingspare.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
