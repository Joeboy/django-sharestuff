from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlquote
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from offers.models import LocalOffer


def user_offer(func):
    """
    Decorator that looks for an offer that has the offer_id passed to the
    function and is owned by the user
    """
    def _inner(request, *args, **kwargs):
        if request.user.is_anonymous():
            path = urlquote(request.get_full_path())
            tup = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
            return HttpResponseRedirect('%s?%s=%s' % tup)

        try:
            offer_id = kwargs.pop('offer_id')
        except KeyError:
            kwargs['offer'] = None
        else:
            kwargs['offer'] = get_object_or_404(LocalOffer, id=offer_id, donor=request.user.get_profile())
        return func(request, *args, **kwargs)
    return _inner
