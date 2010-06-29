from django.contrib.auth.models import User
from django.http import HttpResponseServerError

def userprofile_view(func):
    """
    View decorator that takes the 'username' kwarg passed from the urlconf,
    turns it into a 'userprofile' object and passes that object to the view.
    """
    def _inner(request, *args, **kwargs):
        try:
            user = User.objects.get(username=kwargs.pop('username'))
        except User.DoesNotExist:
            raise Http404('Couldn\'t find user "%s".' % (username,))
        except KeyError:
            return HttpResponseServerError("Improper use of userprofile_view decorator.")

        kwargs['userprofile'] = user.get_profile()
        return func(request, *args, **kwargs)

    return _inner
        

