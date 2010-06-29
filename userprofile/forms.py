from django import forms
from userprofile.models import UserProfile

class UserProfileForm(forms.Form):
    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)

    def clean(self):
        if not self.cleaned_data['latitude'] or not self.cleaned_data['longitude']:
            raise forms.ValidationError("Sorry, you need to enter your location on the map.")
        if self.cleaned_data['latitude'] < 0.865 or \
           self.cleaned_data['latitude'] > 1.1 or \
           self.cleaned_data['longitude'] > 0.04 or \
           self.cleaned_data['longitude'] < -0.187:
            raise forms.ValidationError("Sorry, the location you specified isn't in the British Isles. Please try again.")
        return self.cleaned_data

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = UserProfile
        exclude = ('user', 'commercial',)
