import json
import os
import time
import Image
from hashlib import md5

from django.forms import ModelForm, TextInput
from django.http import HttpResponse
from django.conf import settings

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
            upload_to = LocalOfferImage._meta.get_field_by_name('image')[0].upload_to
            uploaded_file = request.FILES['image']
            filename = md5(str(time.time()) + uploaded_file.name).hexdigest() + '.jpg'
            im = Image.open(uploaded_file)
            width, height = im.size
            if width > 500 or height > 500:
                if width > height:
                    new_width = 500
                    new_height = height * float(500)/width
                else:
                    new_height = 500
                    new_width = width * float(500)/height
                im.thumbnail((int(new_width), int(new_height)), Image.ANTIALIAS)
            im.save(os.path.join(settings.MEDIA_ROOT, upload_to, filename),
                    options={'quality':35})

            offer_image = LocalOfferImage.objects.create(
                image=os.path.join(upload_to, filename),
                caption=form.cleaned_data['caption'],
                offer=offer
                )
            return HttpResponse(json.dumps({'id':offer_image.id,
                                            'url':offer_image.image.url,
                                            'caption':offer_image.caption}))
    else:
        form = LocalImageForm()
    return render_to_response_context(request, 'offers/images/add_image.html', {'form': form, 'form_url':request.path})

