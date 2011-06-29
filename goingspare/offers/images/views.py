import json
from django.forms import ModelForm, TextInput
from django.http import HttpResponse

from offers.models import LocalOfferImage
from offers.decorators import user_offer
from goingspare.utils import render_to_response_context

class LocalImageForm(ModelForm):
    class Meta:
        model = LocalOfferImage
        exclude = ('offer',)
        widgets = {'caption': TextInput}

@user_offer
def add_image(request, offer=None):
    if request.POST:
        form = LocalImageForm(request.POST, request.FILES)
        if form.is_valid():
            im = form.save(commit=False)
            im.offer = offer
            im.save()
            return HttpResponse(json.dumps({'id':im.id, 'url':im.image.url, 'caption':im.caption}))
    else:
        form = LocalImageForm()
    return render_to_response_context(request, 'offers/images/add_image.html', {'form': form, 'form_url':request.path})

