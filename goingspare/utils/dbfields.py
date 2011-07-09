from django import forms
from django.db.models.fields import CharField
from utils.formfields import UKPhoneNumberField as UKPhoneNumberFormField
from django.contrib.localflavor.uk.forms import UKPostcodeField as UKPostcodeFormField

class UKPhoneNumberField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 30)
        super(UKPhoneNumberField, self).__init__(*args, **kwargs)

#    def get_internal_type(self):
#        return "UKPhoneNumberField"

    def formfield(self, **kwargs):
        defaults = {'form_class': UKPhoneNumberFormField}
        defaults.update(kwargs)
        return super(UKPhoneNumberField, self).formfield(**defaults)

class UKPostcodeField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(UKPostcodeField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': UKPostcodeFormField}
        defaults.update(kwargs)
        return super(UKPostcodeField, self).formfield(**defaults)

