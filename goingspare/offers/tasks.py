from django.core import management
from celery.decorators import periodic_task

from datetime import timedelta

@periodic_task(run_every=timedelta(minutes=30))
def scrape():
    management.call_command('scrape_norwichfreegle')
    
