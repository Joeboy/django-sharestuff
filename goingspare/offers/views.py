import re
from itertools import chain

from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms.fields import Field, EMPTY_VALUES
from django.shortcuts import get_object_or_404
from offers.models import LocalOffer, OfferCategory
from django.core.exceptions import PermissionDenied
from userprofile.models import UserProfile

from goingspare.utils import render_to_response_context
from goingspare.offers.decorators import user_offer


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
#    skill_category=RawModelChoiceField(queryset=SkillCategory.objects.all(), widget=CategoryWidget)

    class Meta:
        model = LocalOffer
        exclude = ('donor', 'date_time_added', 'offer_category')


@user_offer
def edit_offer(request, offer=None):
    """
    Edit or create a user's offer
    """
    if request.method == 'POST':
        form = OfferForm(request.POST, instance=offer)
        if form.is_valid():
            offer = OfferForm.save(form, commit=False)
            offer.donor = request.user.get_profile()
            offer.save()
            action = offer and 'edited' or 'created'
            request.user.message_set.create(message="A offer was successfully %s." % action)
            return HttpResponseRedirect(reverse('my-offers'))
    else:
        form = OfferForm(instance=offer)

    return render_to_response_context(request, 'offers/edit_offer.html', {'form': form})


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
    others = request.user.get_profile().watched_users.all()
    offer_sets = [o.offer_set.all() for o in others]
    offers = chain(*offer_sets)
    return render_to_response_context(request,
                                      'offers/others_offers.html',
                                      {'offers':offers})

def contact_re_offer(request, offer_hash):
    raise NotImplementedError
