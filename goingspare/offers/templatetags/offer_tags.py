from django import template
from userprofile.models import UserProfile

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
