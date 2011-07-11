import json

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context

from email_lists.models import EmailList
from userprofile.models import Subscription

from goingspare.utils import render_to_response_context
from offers.decorators import user_offer

class AddEmailListForm(forms.Form):
    email_list = forms.ModelChoiceField(queryset=EmailList.objects.none())
    from_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        userprofile = kwargs.pop('userprofile')
        super(AddEmailListForm, self).__init__(*args, **kwargs)
        users_emaillist_ids = [v['id'] for v in userprofile.email_lists.values('id')]
        self.fields['email_list'].queryset = EmailList.objects.exclude(id__in=users_emaillist_ids)


def add_subscription(request):
    userprofile = request.user.get_profile()

    if request.POST:
        form = AddEmailListForm(request.POST, userprofile=userprofile)
        if form.is_valid():
            subscription = Subscription.objects.create(
                userprofile = request.user.get_profile(),
                email_list = form.cleaned_data['email_list'],
                from_email = form.cleaned_data['from_email']
            )
            return HttpResponseRedirect(reverse('my-offers'))
    else:
        form = AddEmailListForm(initial={'from_email': request.user.email},
                                userprofile=userprofile)

    c = {'form':form}
    return render_to_response_context(request, 'email_lists/add_email_list.html', c)


@user_offer
def get_message(request, offer=None, message_type=None, offer_hash=None):
    t = get_template('email_lists/messages/%s.html' % (message_type))
    c = Context({'userprofile': request.user.get_profile(),
                 'offer': offer, })
    m = t.render(c)
    subject, message = m.split('\n', 1)
    return HttpResponse(json.dumps({'subject': subject, 'message':message}))
