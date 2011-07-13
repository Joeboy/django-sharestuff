import re

from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.forms.fields import Field, EMPTY_VALUES
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.gis.utils import GeoIP
from django.core.exceptions import PermissionDenied

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
def search(request):
    """
    Search for offers
    """
    raise NotImplemented
    return render_to_response_context(request, 'offers/search.html')


@login_required
def my_offers(request):
    """
    Return a list of the user's offers
    """
    return render_to_response_context(request, 'offers/my_offers.html')


class CategoryWidget(forms.TextInput):
    class Media:
        js = ('js/stuff_category_widget.js',)


class RawModelChoiceField(forms.ModelChoiceField):
    def clean(self, value):
        Field.clean(self, value)
        if value in EMPTY_VALUES:
            return None
        if not re.match('^\d+$', value):
            raise forms.ValidationError("Invalid category id")
        try:
            key = self.to_field_name or 'pk'
            value = self.queryset.get(**{key: value})
        except self.queryset.model.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid_choice'])
        return value


class OfferForm(forms.ModelForm):
#    category=RawModelChoiceField(queryset=OfferCategory.objects.all(), widget=CategoryWidget)
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
    userp = request.user.get_profile()
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            offer = OfferForm.save(form, commit=False)
            offer.donor = userp
            offer.longitude = userp.longitude
            offer.latitude = userp.latitude
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
            form = OfferForm(initial={'latitude':userp.latitude,
                                      'longitude':userp.longitude})
        else:
            form = OfferForm(instance=offer, initial={'image_list':','.join([str(im.id) for im in offer.localofferimage_set.all()])})

    return render_to_response_context(request, 'offers/edit_offer.html', {'form': form,
                                                                          'offer': offer,
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
                subscription = form.cleaned_data['subscription'],
                offer = offer,
                message_type = form.cleaned_data['message_type'],
                subject = form.cleaned_data['subject'],
                body = form.cleaned_data['message'],
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



@login_required
def offer_categories(request, parent_id=None):
    """
    Return a list of categories with parent_id=parent_id
    if no parent_id is given return the top level categories
    """
    response=HttpResponse()
    simplejson.dump([(z.id, z.title) for z in OfferCategory.objects.filter(parent=parent_id)], response, ensure_ascii=False)
    return response

@login_required
def offer_category_tree(request, cat_id):
    """
    Redundant category tree
    """
    raise NotImplemented
    cat = get_object_or_404(OfferCategory, id=cat_id);
    tree = []

    while True:
        branches = [(z.id, z.title) for z in OfferCategory.objects.filter(parent=cat.parent)]
        branches.append (cat.id)
        tree.insert(0,branches)
        cat = cat.parent
        if not cat: break
    response=HttpResponse()
    simplejson.dump(tree, response, ensure_ascii=False)
    return response


class OfferFilterForm(forms.Form):
    tags = TagField(required=False)
    watched_users = forms.BooleanField(required=False)
    max_distance = forms.IntegerField(label="Max distance (km)")
    latitude = forms.FloatField(widget=forms.HiddenInput)
    longitude = forms.FloatField(widget=forms.HiddenInput)
    location_source = forms.CharField(widget=forms.HiddenInput)

    TAG_RE = re.compile(r'^[a-zA-Z0-9 -]+$')

    def clean_tags(self, *args, **kwargs):
        # Let's make really, really sure the user
        # isn't able to inject SQL
        tags = self.cleaned_data['tags']
        for tag in tags:
            if not self.TAG_RE.match(tag):
                raise forms.ValidationError('Invalid characters in tag.')
        return tags


def get_offers(**params):
    """
    Evil, evil function to construct sql and grab a filtered queryset
    with added distance field. This function makes no attempt to clean or
    validate its input, so be careful.

    Also, the current sql will scale abysmally and will need redoing
    """
    where = ''
    join = ''
    (latitude,
     longitude,
     max_distance,
     watched_users, ) = (params.get('latitude'),
                         params.get('longitude'),
                         params.get('max_distance'),
                         params.get('watched_users'), )

    if max_distance:
        where += " AND distance <= %d" % (max_distance,)
    if watched_users:
        if params.get('asking_userprofile'):
            asking_userprofile = params['asking_userprofile']
        else:
            raise PermissionDenied
        where += ' and donor_id in (select to_userprofile_id from userprofile_userprofile_watched_users where from_userprofile_id=%s)' % asking_userprofile.id
    if params.get('tags'):
        tag_str = ", ".join(["E'%s'" % t for t in params['tags']])
        join = """
INNER JOIN taggit_taggeditem ON (p.id = taggit_taggeditem.object_id) INNER JOIN taggit_tag ON (taggit_taggeditem.tag_id = taggit_tag.id)"""
        where += """ and (taggit_tag.name IN (%s) AND taggit_taggeditem.content_type_id = %d)""" % (tag_str, LOCALOFFER_CTYPE)

    sql = "select * from (select *, earth_distance(ll_to_earth(%s, %s), ll_to_earth(latitude, longitude))/1000 AS distance from offers_localoffer) as p %s WHERE TRUE %s" % (latitude, longitude, join, where)

    return LocalOffer.objects.raw(sql)


@login_required
def others_offers(request):
    """
    List of offers from watched users
    Be very careful to validate the input to get_offers
    """
    userprofile = request.user.get_profile()

    if request.POST:
        form = OfferFilterForm(request.POST)
        if form.is_valid():
            offers = get_offers(latitude=form.cleaned_data['latitude'],
                                longitude = form.cleaned_data['longitude'],
                                watched_users=form.cleaned_data['watched_users'],
                                asking_userprofile = userprofile,
                                tags=form.cleaned_data['tags'],
                                max_distance=form.cleaned_data['max_distance'])
        else:
            if request.is_ajax():
                return JsonResponse({'errors':form.errors})
            else:
                return render_to_response_context(
                    request,
                    'offers/others_offers.html',
                    {'form':form,
                     'offers':[]})
    else:
        if userprofile.latitude and userprofile.longitude:
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
        form = OfferFilterForm(initial={'max_distance': 25,
                                        'latitude':lat,
                                        'longitude':lon,
                                        'location_source':location_source})
        offers = []

    if request.is_ajax():
        data = {'offers': [{'id':o.id,
                            'title':o.title,
                            'description':o.description,
                            'distance':o.distance,
                            'hash':o.hash,
                            'donor_name': o.donor.get_best_name()} for o in offers]}

        return JsonResponse(data)
    else:
        return render_to_response_context(request,
                                          'offers/others_offers.html',
                                          {'form':form,
                                           'offers':offers})


def user_offers(request, username):
    donor = get_object_or_404(UserProfile, user__username=username)
    offers = LocalOffer.objects.filter(donor=donor)
    return render_to_response_context(request,
                                      'offers/user_offers.html',
                                      {'offers':offers,
                                       'donor':donor})
    
#@login_required
#def xxxothers_offers(request):
#    """
#    redundant, I think
#    List of offers from watched users
#    Be very careful to validate the input to build_select
#    """
#    if True or request.is_ajax():
#        return others_offers_ajax(request)
#
#    userprofile = request.user.get_profile()
#
#
#    if request.POST:
#        form = OfferFilterForm(request.POST)
#        if form.is_valid():
#            sql = build_select(userprofile,
#                               watched_users=form.cleaned_data['watched_users'],
#                               tags=form.cleaned_data['tags'],
#                               max_distance=form.cleaned_data['max_distance'])
#            offers = LocalOffer.objects.raw(sql)
#        else:
#            offers = None
#    else:
#        if userprofile.latitude and userprofile.longitude:
#            lat, lon = userprofile.latitude, userprofile.longitude
#            location_source = 'userprofile'
#        else:
#            g = GeoIP()
#            ip = request.META.get('REMOTE_ADDR')
#            lat, lon = 52.63639666, 1.29432678223
#            location_source = 'none'
#            if ip:
#                latlon = g.lat_lon(ip)
#                if latlon:
#                    lat, lon = latlon
#                    location_source = 'ip'
#        form = OfferFilterForm(initial={'max_distance': 25,
#                                        'latitude':lat,
#                                        'longitude':lon,
#                                        'location_source':location_source})
#        offers = None
#
#    return render_to_response_context(request,
#                                      'offers/others_offers.html',
#                                      {'form':form,
#                                       'offers':offers})

def view_offer(request, offer_hash):
    offer = get_object_or_404(LocalOffer, hash=offer_hash)
    return render_to_response_context(request,
                                      'offers/offer.html',
                                      {'offer':offer})

class OfferContactForm(forms.Form):
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
                                      {'offer_contact_form':form})

def offer_contact_sent(request):
    return render_to_response_context(request,
                                      'offers/offer_contact_sent.html')
