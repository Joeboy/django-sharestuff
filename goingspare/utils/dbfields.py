from django import forms
from django.db.models.fields import CharField
from utils.formfields import UKPhoneNumberField as UKPhoneNumberFormField

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

