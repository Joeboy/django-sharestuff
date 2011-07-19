from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms

from goingspare.utils import render_to_response_context
from userprofile.models import UserProfile
from offers.models import LocalOffer

OFFERS_PER_PAGE = 15

def index(request):
    userprofile = UserProfile.get_for_user(request.user)
    offers = LocalOffer.objects.filter_by_user(userprofile)
    if userprofile and userprofile.location:
        offers = offers.distance(userprofile.location)
    paginator = Paginator(offers, OFFERS_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        page = paginator.page(request.GET.get('page', 1))
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        page = paginator.page(1)
    return render_to_response_context(request,
                                      'index.html',
                                      {'page': page})
