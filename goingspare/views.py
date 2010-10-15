from goingspare.utils import render_to_response_context
from django.db import connection
from django import forms

def index(request):
    return render_to_response_context(request, 'index.html')
