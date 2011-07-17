import os
import sys
import ClientCookie
import ClientForm
import re
from pyquery import PyQuery
import lxml
from datetime import datetime
import re
from django.conf import settings
from django.core.management.base import BaseCommand
from offers.models import LocalOffer
from optparse import make_option
from geo.models import Outcode
from django.contrib.auth.models import User


def grab(test=False):
    if test and os.path.exists('cache.html'):
        print "Using cached html page"
        f = open('cache.html')
        data = f.read()
        f.close()
    else:
        # Create special URL opener (for User-Agent) and cookieJar
        cookieJar = ClientCookie.CookieJar()
        opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
        opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
        ClientCookie.install_opener(opener)
        fp = ClientCookie.urlopen("http://login.yahoo.com")
        forms = ClientForm.ParseResponse(fp)
        fp.close()

        form = forms[0]
        form["login"]  = settings.YAHOOGROUPS_USERNAME
        form["passwd"] = settings.YAHOOGROUPS_PASSWORD
        fp = ClientCookie.urlopen(form.click())
        fp.close()
        fp = ClientCookie.urlopen("http://groups.yahoo.com/group/norwichfreegle/messages") # use your group
        data = ''.join(fp.readlines())
        fp.close()
    if test:
        f = open('cache.html', 'w')
        f.write(data)
        f.close()
    return data


def get_offers(html):
    parser = lxml.etree.HTMLParser()
    html = html.decode("iso-8859-1")
    root = lxml.html.fromstring(html)

    DATE_GRAB = re.compile('<td[^>]*>(.*?)(<br>(.*))?</td>', re.S | re.M)

    today = datetime.now().strftime('%b %d, %Y')

    def clean(s):
        return s.strip().replace('&#160;', ' ')

    offers = []
    for e in root.cssselect('td.message'):
#        title = e.cssselect('a span')[0].text
        title = e.cssselect('a span')[0].text_content()
        row = e.getparent()
        date_el = row.cssselect('td.date')[0]
        match = DATE_GRAB.search(lxml.html.tostring(date_el))
        groups = match.groups()
        if groups[1]:
            date = clean(groups[0])
            time = clean(groups[2])
        else:
            date = today
            time = clean(groups[0])
        dts = "%s %s" % (date, time)
        dt = datetime.strptime(dts, '%b %d, %Y %I:%M %p')
        offers.append((dt, title))
    return offers


def load_offers(offers):
    offer_re = re.compile(r'^offer(?:ed)?\b\s*:?-?\s*(.*)\s*$', re.I)
    postcode_re = re.compile(r'\b(NR\d+)\b')
    freegle_up = User.objects.get(username='norwichfreegle').get_profile()
#    LocalOffer.objects.filter(donor=freegle_up).delete()
    for offer in offers:
        match = offer_re.match(offer[1])
        if not match:
            continue
        title = match.group(1)
        match = postcode_re.search(title)
        if not match:
            continue
        try:
            outcode = Outcode.objects.get(outcode=match.group(1))
        except Outcode.DoesNotExist:
            continue
        o = LocalOffer.objects.get_or_create(title=title,
                                             donor=freegle_up,
                                             description="Description not available",
                                             latitude=outcode.lat,
                                             longitude=outcode.lng,
                                             date_time_added=offer[0],
                                             list_sharestuffers=True,
                                             show_sharestuffers=True)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--testrun',
            action='store_true',
            dest='testrun',
            default=False,
            help="Use cached html, if available"),
        )

    def handle(self, *args, **options):
        html = grab(options['testrun'])
        offers = get_offers(html)
        load_offers(offers)

