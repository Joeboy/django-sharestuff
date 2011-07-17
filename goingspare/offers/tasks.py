from celery.decorators import task
from django.core import management

@task()
def scrape():
    print "doing the task!"
    management.call_command('scrape_norwichfreecycle')
    
