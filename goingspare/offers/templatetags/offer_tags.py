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

    def page_link_tag(page, contents):
        return '<a href="%s">%s</a>' % (link_to_page(page), unicode(contents))

    page = context.get('page')
    if page is None:
        return ''
    page_no = page.number
    if page.paginator.num_pages == 1:
        return ''
    request = context['request']
    reqvars = dict(request.REQUEST)

    if page.has_previous():
        prev = page_link_tag(page.previous_page_number(), 'Prev')
    else:
        prev = ''

    if page.has_next():
        next = page_link_tag(page.next_page_number(), 'Next')
    else:
        next = ''

    page_links = ' '.join([
        ((p == page_no) and unicode(p) or page_link_tag(p, unicode(p)))
            for p in page.paginator.page_range])

    return '<p class="pagination-bar">%s %s %s</p>' % (prev, page_links, next)
