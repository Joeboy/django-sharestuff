from django.db import connection
from django import forms

from goingspare.utils import render_to_response_context
from userprofile.models import UserProfile
from offers.models import LocalOffer

def index(request):
    userprofile = UserProfile.get_for_user(request.user)
    offers = LocalOffer.objects.filter_by_user(userprofile)
    return render_to_response_context(request,
                                      'index.html',
                                      {'offers': offers})
