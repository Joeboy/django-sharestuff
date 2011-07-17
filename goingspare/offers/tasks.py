from .importing.scrape_norwichfreegle import grab, get_offers
from celery.decorators import task

@task()
def scrape():
    print "doing the task!"
    html = grab()
    offers = get_offers(html)
    print offers
    
