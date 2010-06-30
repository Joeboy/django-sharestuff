from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from userprofile.decorators import userprofile_view

@userprofile_view
def user_offer_list(request, userprofile=None):
    context_instance=RequestContext(request, {'userprofile':userprofile} )

    return render_to_response('offers/user_offer_list.html',
                              context_instance=context_instance)

