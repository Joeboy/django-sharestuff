from django import forms
from django.forms.models import inlineformset_factory
from offers.models import Offer, OfferImage
from userprofile.models import UserProfile

class UserProfileForm(forms.ModelForm):
    """
    Form to allow registered users to edit their profile info.
    Includes extra email field as that goes in User, not UserProfile.
    """
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        exclude = ('user', 'commercial',)

    def clean(self):
        if not self.cleaned_data['latitude'] or not self.cleaned_data['longitude']:
            raise forms.ValidationError("Sorry, you need to enter your location on the map.")
#        if self.cleaned_data['latitude'] < 0.865 or \
#           self.cleaned_data['latitude'] > 1.1 or \
#           self.cleaned_data['longitude'] > 0.04 or \
#           self.cleaned_data['longitude'] < -0.187:
#            raise forms.ValidationError("Sorry, the location you specified isn't in the British Isles. Please try again.")
        return self.cleaned_data


class OfferForm(forms.ModelForm):
    """
    A form that allows a user to add/edit an offer
    """
    class Meta:
        model = Offer
        exclude=('taken_status_other', 'regular', 'donor', 'date_time_added')


OfferImageFormSet = inlineformset_factory(Offer, OfferImage, can_delete=True,
                                          extra=1, exclude=('thumbnail',))


