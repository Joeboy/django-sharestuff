from django.forms import ValidationError
from django.forms.fields import CharField, EMPTY_VALUES
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
import re
import types

class UKPhoneNumberField(CharField):
    default_error_messages = {
        'partial': _('Phone number must include an area code.'),
        'non_uk': _('Phone number must be a UK number.'),
        'length_range': _('Phone number must be between %d and %d digits'),
        'length': _('Phone number must be %d digits'),
        'reject_premium': _('Phone number can\'t be premium rate.'),
        'reject_service': _('Phone number can\'t be a service number.')
    }
    
    number_specs = (
        (r'^01(1[^1]|[^1]1)',      None,     (4, 3, 4)),
        (r'^01',                   None,     (5, (5, 6))),
        (r'^0500',                 None,     (4, 6)),
        (r'^0[235]',               None,     (3, 4, 4)),
        (r'^07',                   None,     (5, 6)),
        (r'^(08001111|08454647)$', None,     (4, 4)),
        (r'^08',                   None,     (4, 7)),
        (r'^09',                  'premium', (4, 6)),
        (r'^118',                 'service', (3, 3)),
        (r'^999$',                'service', (3,)),
        (r'^1',                   'service', None),
    )
    
    def __init__(self, *args, **kwargs):
        self.reject = set(kwargs.pop('reject', ()))
        super(UKPhoneNumberField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        super(UKPhoneNumberField, self).clean(value)
        
        value = smart_unicode(value)
        
        if value in EMPTY_VALUES:
            return u''
        
        value = re.sub(r'[^0-9+]',        r'',  value)
        value = re.sub(r'(?<!^)\+',       r'',  value)
        value = re.sub(r'^\+44(?=[1-9])', r'0', value)
        value = re.sub(r'^\+44(?=0)',     r'',  value)
        
        if re.match(r'^(\+(?!44)|00)', value):
            raise ValidationError(self.error_messages['non_uk'])
        
        number_spec = self.get_number_spec(value)
        
        if not number_spec:
            raise ValidationError(self.error_messages['partial'])
        
        if number_spec[0] in self.reject:
            raise ValidationError(self.error_messages['reject_%s' % number_spec[0]])
        
        if not self.valid_length(value, number_spec):
            min_length, max_length = self.spec_lengths(number_spec)
            if min_length == max_length:
                raise ValidationError(self.error_messages['length']
                    % min_length)
            else:
                raise ValidationError(self.error_messages['length_range']
                    % (min_length, max_length))
        
        return self.format_number(value, number_spec)
    
    def get_number_spec(self, value):
        for number_spec in self.number_specs:
            if re.match(number_spec[0], value):
                return number_spec[1:]
        return None
    
    def spec_lengths(self, number_spec):
        if not number_spec[1]:
            return None, None
        if type(number_spec[1][-1]) == types.TupleType:
            min_length, max_length = number_spec[1][-1]
            total = sum(number_spec[1][:-1])
            min_length += total
            max_length += total
        else:
            min_length = max_length = sum(number_spec[1])
        return min_length, max_length
    
    def valid_length(self, value, number_spec):
        min_length, max_length = self.spec_lengths(number_spec)
        if min_length is not None and len(value) < min_length: return False
        if max_length is not None and len(value) > max_length: return False
        return True
    
    def format_number(self, value, number_spec):
        if number_spec[1] is None:
            components = (value,)
        else:
            components = []
            position = 0
            last_index = len(number_spec) - 1
            for index, chunk in enumerate(number_spec[1]):
                if index == last_index:
                    components.append(value[position:])
                else:
                    components.append(value[position:position+chunk])
                    position += chunk
        return ' '.join(components)

