from functools import wraps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlquote
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from offers.models import LocalOffer


def user_offer(func):
    """
    Decorator that looks for an offer that has the offer_id or offer_hash
    passed to the function and is owned by the user
    """
    @wraps(func)
    def _inner(request, *args, **kwargs):
        if request.user.is_anonymous():
            path = urlquote(request.get_full_path())
            tup = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
            return HttpResponseRedirect('%s?%s=%s' % tup)

        offer_spec = {}
        for k in ('offer_id', 'offer_hash'):
            try:
                offer_spec[k[6:]] = kwargs.pop(k)
            except KeyError:
                continue
        if offer_spec:
            offer_spec['donor'] = request.user.get_profile()
            kwargs['offer'] = get_object_or_404(LocalOffer, **offer_spec)
        else:
            kwargs['offer'] = None
        return func(request, *args, **kwargs)
    return _inner
