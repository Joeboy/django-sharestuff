import re

from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.forms.fields import Field, EMPTY_VALUES
from django.forms.util import ErrorList
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.gis.utils import GeoIP
from django.core.exceptions import PermissionDenied
from django.template.loader import get_template
from django.template import RequestContext

from taggit.forms import TagField

from offers.models import LocalOffer, OfferCategory, LocalOfferImage
from userprofile.models import UserProfile, Subscription

from goingspare.utils import render_to_response_context
from goingspare.utils.http import JsonResponse
from goingspare.offers.decorators import user_offer
from notifications.models import Notification
from email_lists.models import EmailMessage

CSV_RE = re.compile(r'^[\d,]*$')
LOCALOFFER_CTYPE = ContentType.objects.get_for_model(LocalOffer).pk


@login_required
def my_offers(request):
    """
    Return a list of the user's offers
    """
    return render_to_response_context(request, 'offers/my_offers.html')


class OfferForm(forms.ModelForm):
    image_list = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_image_list(self):
        il = self.cleaned_data['image_list']
        if not CSV_RE.match(il):
            raise forms.ValidationError('There was an error to do with the list of images attached to your post.')
        image_ids = filter(len, il.split(','))
        images = LocalOfferImage.objects.filter(id__in=image_ids)
        if len(images) != len(image_ids):
            raise forms.ValidationError, "There was some kind of problem."
        return images

    class Meta:
        model = LocalOffer
        exclude = ('donor', 'date_time_added', 'offer_category', 'hash', 'longitude', 'latitude')

    class Media:
        js = ('js/edit_offer.js',)


@user_offer
def edit_offer(request, offer=None):
    """
    Edit or create a user's offer
    """
    userprofile = request.user.get_profile()
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            offer = OfferForm.save(form, commit=False)
            offer.donor = userprofile
            offer.longitude = userprofile.longitude
            offer.latitude = userprofile.latitude
            offer.save()
            form.save_m2m()
            for im in form.cleaned_data['image_list']:
                im.offer = offer
                im.save()
            action = offer and 'edited' or 'created'
            request.user.message_set.create(message="A offer was successfully %s." % action)
            return HttpResponseRedirect(reverse('my-offers'))
    else:
        if offer is None:
            initial = {'latitude': userprofile.latitude,
                     'longitude': USERPROFILE.LONGITUDE}
            for action in 'list', 'show':
                for who in 'public', 'sharestuffers', 'watchers':
                    initial['%s_%s' % (action, who)] = getattr(userprofile, 'offers_%s_%s' % (action, who))

            form = OfferForm(initial=initial)
            initial['list_public'] = userprofile.offers_list_public
        else:
            form = OfferForm(instance=offer, initial={'image_list': ','.join([str(im.id) for im in offer.localofferimage_set.all()])})

    privacy_fields = [form.fields[k] for k in ('list_public', 'list_sharestuffers', 'list_watchers')]
    return render_to_response_context(request, 'offers/edit_offer.html', {'form': form,
                                                                          'offer': offer,
                                                                          'privacy_fields': privacy_fields,
                                                                          'image_list': offer and offer.image_list or '[]'})


@user_offer
def delete_offer(request, offer):
    """
    Delete a user's offer
    """
    if request.GET.get('confirm') == 'yes':
        offer.delete()
        request.user.message_set.create(message="An offer was deleted.")
        return HttpResponseRedirect(reverse('my-offers'))
    elif request.GET.get('confirm') == 'no':
        request.user.message_set.create(message="Deletion of offer cancelled.")
        return HttpResponseRedirect(reverse('my-offers'))
    else:
        return render_to_response_context(request, 'offers/confirm_delete_offer.html')


MESSAGE_TYPE_CHOICES = ((0, '-------'), ('offer', 'Offer'), ('taken', 'Taken'),)


class EmailOfferToListForm(forms.Form):
    subscription = forms.ModelChoiceField(queryset=Subscription.objects.none())
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    message_type = forms.ChoiceField(choices=MESSAGE_TYPE_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        userprofile = kwargs.pop('userprofile')
        super(EmailOfferToListForm, self).__init__(*args, **kwargs)
        self.fields['subscription'].queryset = userprofile.subscription_set.all()


@user_offer
def email_offer_to_list(request, offer):
    userprofile = request.user.get_profile()
    if request.POST:
        form = EmailOfferToListForm(request.POST, userprofile=userprofile)
        if form.is_valid():
            msg = EmailMessage(
                subscription=form.cleaned_data['subscription'],
                offer=offer,
                message_type=form.cleaned_data['message_type'],
                subject=form.cleaned_data['subject'],
                body=form.cleaned_data['message'],
            )
            msg.save()
            msg.send_mail()
            return HttpResponseRedirect(reverse('my-offers'))
    else:
        initial = {}
        if userprofile.subscription_set.count() == 1:
            initial['subscription'] = userprofile.subscription_set.get()
        form = EmailOfferToListForm(userprofile=request.user.get_profile(),
                                    initial=initial)
    c = {'offer': offer,
         'form': form}
    return render_to_response_context(request, 'offers/email_offer_to_list.html', c)


class OfferListForm(forms.Form):
    """
    Form for getting a specified list of offers
    """
    tags = TagField(required=False)
    watched_users = forms.BooleanField(required=False)
    latitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    max_distance = forms.IntegerField(label="Max distance (km)", required=False)
    donor = forms.CharField(required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('donor'):
            try:
                cleaned_data['donorprofile'] = UserProfile.objects.get(user__username=cleaned_data['donor'])
            except UserProfile.DoesNotExist:
                self._errors['donor'] = ErrorList(['No such user'])
        else:
            cleaned_data['donorprofile'] = None

        return cleaned_data


class OfferBrowseForm(OfferListForm):
    """
    Subclass of OfferListForm with an added field used to keep track of what
    source has been used to divine the user's location
    """
    location_source = forms.ChoiceField(widget=forms.HiddenInput, choices=(
            ('userprofile', 'userprofile'),
            ('browser', 'browser'),
            ('ip', 'ip')))


def list_offers(request):
    """
    Sorta the same as browse_offers, but for direct linking rather than
    filtering via a form
    """
    if request.user.is_authenticated():
        userprofile = request.user.get_profile()
        lat, lon = userprofile.latitude, userprofile.longitude
    else:
        userprofile = None
        lat, lon = None, None

    # Merge POST input with GET input - GET gets precendence
    input = request.POST.copy()
    input.update(dict([(f, request.GET.get(f)) for f in OfferListForm.base_fields if f in request.GET]))
    form = OfferListForm(input)

    if form.is_valid():
        latitude = form.cleaned_data['latitude']
        longitude = form.cleaned_data['longitude']
        if None in (latitude, longitude):
            latitude, longitude = lat, lon
        offers = LocalOffer.objects.filter_by(
            donorprofile=form.cleaned_data['donorprofile'],
            watched_users=form.cleaned_data['watched_users'],
            latitude=latitude,
            longitude=longitude,
            asking_userprofile=userprofile,
            tags=form.cleaned_data['tags'],
            max_distance=form.cleaned_data['max_distance'])

        c = RequestContext(request, {'offers': offers})
        if request.is_ajax():
            t = get_template('offers/list_offers_nochrome.html')
            return JsonResponse({'html': t.render(c)})
        else:
            t = get_template('offers/list_offers.html')
            return HttpResponse(t.render(c))
    else:
        # TODO
        print form.errors
        for e in form.errors:
            print e
        return HttpResponse("invalid")


def browse_offers(request):
    """
    """
    if request.user.is_authenticated():
        userprofile = request.user.get_profile()
    else:
        userprofile = None

    if request.method == 'POST':
        if request.is_ajax():
            return list_offers(request)

        form = OfferBrowseForm(request.POST)
        if form.is_valid():
            offers = LocalOffer.objects.filter_by(
                latitude=form.cleaned_data['latitude'],
                longitude=form.cleaned_data['longitude'],
                watched_users=form.cleaned_data['watched_users'],
                asking_userprofile=userprofile,
                tags=form.cleaned_data['tags'],
                max_distance=form.cleaned_data['max_distance'])
        else:
            if request.is_ajax():
                return JsonResponse({'errors': form.errors})
            else:
                return render_to_response_context(
                    request,
                    'offers/browse_offers.html',
                    {'form': form,
                     'offers': []})
    else:
        if userprofile and userprofile.latitude and userprofile.longitude:
            lat, lon = userprofile.latitude, userprofile.longitude
            location_source = 'userprofile'
        else:
            g = GeoIP()
            ip = request.META.get('REMOTE_ADDR')
            lat, lon = 52.63639666, 1.29432678223
            location_source = 'none'
            if ip:
                latlon = g.lat_lon(ip)
                if latlon:
                    lat, lon = latlon
                    location_source = 'ip'
        form = OfferBrowseForm(initial={'max_distance': 25,
                                        'latitude': lat,
                                        'longitude': lon,
                                        'location_source': location_source})
        offers = []

    if request.is_ajax():
        data = {'offers': [{'id': o.id,
                            'title': o.title,
                            'description': o.description,
                            'distance': o.distance,
                            'hash': o.hash,
                            'donor_name': o.donor.get_best_name()} for o in offers]}

        return JsonResponse(data)
    else:
        return render_to_response_context(request,
                                          'offers/browse_offers.html',
                                          {'form': form,
                                           'offers': offers})


def user_offers(request, username):
    donor = get_object_or_404(UserProfile, user__username=username)
    offers = LocalOffer.objects.filter(donor=donor)
    return render_to_response_context(request,
                                      'offers/user_offers.html',
                                      {'offers': offers,
                                       'donor': donor})


def view_offer(request, offer_hash):
    offer = get_object_or_404(LocalOffer, hash=offer_hash)
#    if request.user.is_anonymous() and not offer.show_public:
#    TODO
    return render_to_response_context(request,
                                      'offers/offer.html',
                                      {'offer': offer})


class OfferContactForm(forms.Form):
    """
    Form for contacting a user about an offer
    """
    message = forms.CharField(widget=forms.Textarea)

MESSAGE_TEMPLATE = """
<p>User <a href="%s">%s</a> contacted you about your offer <a href="%s">%s</a>:</p>

%s
"""


@transaction.commit_on_success
def offer_contact(request, offer_hash):
    offer = get_object_or_404(LocalOffer, hash=offer_hash)
    if request.POST:
        form = OfferContactForm(request.POST)
        if form.is_valid():
            sender = request.user.get_profile()
            sender_url = sender.get_absolute_url()
            message = MESSAGE_TEMPLATE % (sender_url,
                                          sender.get_best_name(),
                                          offer.get_absolute_url(),
                                          offer.title,
                                          form.cleaned_data['message'])
            n = Notification.objects.create(to_user=offer.donor,
                                            message=message)
            send_mail('Sharestuff: enquiry about "%s"' % offer.title, message, 'no_reply@sharestuff.org.uk',
                      [offer.donor.user.email], fail_silently=False)
            return HttpResponseRedirect(reverse('offer-contact-sent'))
    else:
        form = OfferContactForm()

    return render_to_response_context(request,
                                      'offers/contact_form.html',
                                      {'offer_contact_form': form})


def offer_contact_sent(request):
    return render_to_response_context(request,
                                      'offers/offer_contact_sent.html')
