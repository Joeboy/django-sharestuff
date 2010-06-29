from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from things.models import Thing
from django.contrib.auth.models import User

def user_stuff_list(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404('Couldn\'t find user "%s".' % (username,))

    userprofile = user.get_profile()
    context_instance=RequestContext(request, {'userprofile':userprofile} )

    return render_to_response('things/user_stuff_list.html',
                              context_instance=context_instance)

