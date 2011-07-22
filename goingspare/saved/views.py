import urllib

from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.db import transaction

from .models import SavedFilter
from goingspare.utils import render_to_response_context, get_random_hash
from userprofile.models import UserProfile

class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        exclude = ('slug', )

    def __init__(self, *args, **kwargs):
        super(SavedSearchForm, self).__init__(*args, **kwargs)
        del self.fields['owner']
        for f in ('donor', 'location', 'max_distance', 'watched_users', 'tags'):
            self.fields[f].widget = forms.HiddenInput()

def unique_slug(name):
    return '%s-%s' % (slugify(name), get_random_hash())


@transaction.commit_on_success
def save(request):
    userprofile = UserProfile.get_for_user(request.user)
    if not userprofile:
        raise PermissionDenied
    if request.POST:
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            saved_search = form.save(commit=False)
            saved_search.slug = unique_slug(form.cleaned_data['name'])
            saved_search.owner = userprofile
            saved_search.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('browse-offers'))
    else:
        initial = {}
        if request.GET.get('donor'):
            initial['donor'] = get_object_or_404(UserProfile, user__username=request.GET['donor'])
        if request.GET.get('max_distance'):
            initial['max_distance'] = request.GET['max_distance']
        if request.GET.get('watched_users'):
            initial['watched_users'] = request.GET['watched_users']
        try:
            longitude, latitude = (float(request.GET['longitude']),
                                   float(request.GET['latitude']))
            initial['location'] = Point(longitude, latitude)
        except (KeyError, TypeError, ValueError):
            pass
        form = SavedSearchForm(initial=initial)

    return render_to_response_context(request,
                                      "saved/save_search.html", 
                                      {'form': form});

from offers.views import list_offers

def saved(request, filter_slug):
    # TODO:Make this return a list directly rather than redirecting
    saved_filter = get_object_or_404(SavedFilter, slug=filter_slug)
#    print [(k, getattr(saved_filter,k)) for k in ('donor', 'location', 'max_distance', 'watched_users', 'tags')]
    spec = {}
    if saved_filter.donor:
        spec['donor'] = saved_filter.donor.user.username
    if saved_filter.location:
        spec['longitude'], spec['latitude'] = saved_filter.location.coords
    if saved_filter.max_distance:
        spec['max_distance'] = saved_filter.max_distance
    if saved_filter.watched_users:
        spec['watched_users'] = saved_filter.watched_users
    # TODO: tags

    qs = urllib.urlencode(spec)
    return HttpResponseRedirect('%s?%s' % (reverse('list-offers'), qs))
