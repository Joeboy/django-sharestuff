import random

from django.shortcuts import render_to_response
from django.template import RequestContext

def render_to_response_context(request, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(request)
    return render_to_response(*args, **kwargs)


B36_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'


def get_random_hash():
    number = random.getrandbits(64)
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = B36_ALPHABET[i] + base36
    return base36 or B36_ALPHABET[0]


