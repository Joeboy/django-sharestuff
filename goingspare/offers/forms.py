import re

from django import forms
from django.forms.util import ErrorList
from taggit.forms import TagField

from offers.models import LocalOffer, LocalOfferImage
from userprofile.models import UserProfile, Subscription


CSV_RE = re.compile(r'^[\d,]*$')


class OfferForm(forms.ModelForm):
    image_list = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_image_list(self):
        il = self.cleaned_data['image_list']
        if not CSV_RE.match(il):
            raise forms.ValidationError('There was an error to do with the list of images attached to your post.')
        image_ids = filter(len, il.split(','))
        images = LocalOfferImage.objects.filter(id__in=image_ids)
        if len(images) != len(image_ids):
            raise forms.ValidationError, "There was some kind of problem."
        return images

    class Meta:
        model = LocalOffer
        exclude = ('donor', 'date_time_added', 'offer_category', 'hash', 'longitude', 'latitude')

    class Media:
        js = ('js/edit_offer.js',)


MESSAGE_TYPE_CHOICES = ((0, '-------'), ('offer', 'Offer'), ('taken', 'Taken'),)


class EmailOfferToListForm(forms.Form):
    subscription = forms.ModelChoiceField(queryset=Subscription.objects.none())
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    message_type = forms.ChoiceField(choices=MESSAGE_TYPE_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        userprofile = kwargs.pop('userprofile')
        super(EmailOfferToListForm, self).__init__(*args, **kwargs)
        self.fields['subscription'].queryset = userprofile.subscription_set.all()


class OfferListForm(forms.Form):
    """
    Form for getting a specified list of offers
    """
    tags = TagField(required=False)
    watched_users = forms.BooleanField(required=False)
    latitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput, required=False)
    max_distance = forms.IntegerField(label="Max distance (km)", required=False)
    donor = forms.CharField(required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('donor'):
            try:
                cleaned_data['donorprofile'] = UserProfile.objects.get(user__username=cleaned_data['donor'])
            except UserProfile.DoesNotExist:
                self._errors['donor'] = ErrorList(['No such user'])
        else:
            cleaned_data['donorprofile'] = None

        return cleaned_data


class OfferBrowseForm(OfferListForm):
    """
    Subclass of OfferListForm with an added field used to keep track of what
    source has been used to divine the user's location
    """
    location_source = forms.ChoiceField(widget=forms.HiddenInput, choices=(
            ('userprofile', 'userprofile'),
            ('browser', 'browser'),
            ('ip', 'ip'),
            ('none', 'none')))


class OfferContactForm(forms.Form):
    """
    Form for contacting a user about an offer
    """
    message = forms.CharField(widget=forms.Textarea)
