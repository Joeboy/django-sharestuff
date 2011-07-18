from django import template
from userprofile.models import UserProfile
from urllib import urlencode

register = template.Library()


@register.tag
def ifshowoffertouser(parser, token):
    nodelist_true = parser.parse(('else', 'endifshowoffertouser'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifshowoffertouser',))
        parser.delete_first_token()
    else:
        nodelist_false = template.base.NodeList()
    return ShowOfferToUserNode(nodelist_true, nodelist_false)


class ShowOfferToUserNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def render(self, context):
        userprofile = UserProfile.get_for_user(context['user'])
        if context['offer'].show_to_user(userprofile):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

@register.simple_tag(takes_context=True)
def pagination_bar(context):
    def link_to_page(page):
        reqvars['page'] = page
        return "%s?%s" % (request.path, urlencode(reqvars))

    request = context['request']
    reqvars = dict(context['request'].REQUEST)#.copy()
    page = context.get('page')
    if page is None:
        return ''
    try:
        page_no = int(reqvars['page'])
    except KeyError, ValueError:
        page_no = 1

    if page.has_previous():
        prev = '<a href="%s">Prev</a>' % (link_to_page(page.previous_page_number()),)
    else:
        prev = ''

    if page.has_next():
        next = '<a href="%s">Next</a>' % (link_to_page(page.next_page_number()),)
    else:
        next = ''
    if prev and next:
        return '%s | %s' % (prev, next)
    else:
        return prev or next
    
