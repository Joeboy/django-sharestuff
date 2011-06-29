import re
import json
from itertools import chain

from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms.fields import Field, EMPTY_VALUES
from django.shortcuts import get_object_or_404
from offers.models import LocalOffer, OfferCategory, LocalOfferImage
from django.core.exceptions import PermissionDenied
from django.db import connection, transaction
from userprofile.models import UserProfile

from goingspare.utils import render_to_response_context
from goingspare.offers.decorators import user_offer
from notifications.models import Notification

CSV_RE = re.compile(r'^[\d,]*$')

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
    image_list = forms.CharField(widget=forms.HiddenInput)

    def clean_image_list(self):
        il = self.cleaned_data['image_list']
        if not CSV_RE.match(il):
            raise forms.ValidationError('There was an error to do with the list of images attached to your post.')
        image_ids = il.split(',')
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


@login_required
def others_offers(request):
    """
    List of offers from watched users
    """
    cursor = connection.cursor()
    userp = request.user.get_profile()
    sql = """
SELECT title,
       donor_id,
       hash,
       earth_distance(ll_to_earth(%s, %s), ll_to_earth(latitude, longitude))/1000
FROM offers_localoffer where donor_id in (select to_userprofile_id from userprofile_userprofile_watched_users where from_userprofile_id=%s)
    """
    cursor.execute(sql, (userp.latitude, userp.longitude, userp.id))
    offers = [{'title':row[0], 'donor':UserProfile.objects.get(id=row[1]), 'hash':row[2], 'distance':row[3]} for row in cursor.fetchall()]
    return render_to_response_context(request,
                                      'offers/others_offers.html',
                                      {'offers':offers})

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
