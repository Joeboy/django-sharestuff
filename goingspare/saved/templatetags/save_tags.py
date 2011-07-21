from django import template
from django.core.urlresolvers import reverse
#from userprofile.models import UserProfile
from urllib import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def save_search(context):
    path = reverse('save-search')
    vars = ('donor',
            'tags',
            'watched_users',
            'longitude',
            'latitude',
            'max_distance')
    reqvars = context['request'].REQUEST
    reqvars = dict([(k, reqvars[k]) for k in vars if reqvars.get(k)])
    return '%s?%s' % (path, urlencode(reqvars))
