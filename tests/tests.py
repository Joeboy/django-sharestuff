from django.test import TestCase
from django.test.client import Client
from django.core import mail
import re

class GlobalTest(TestCase):
    """
    Functional tests that don't belong to specific apps
    """

    def test_01_homepage(self):
        client = Client()
        response = client.get('/')
        self.assertContains(response, 'Welcome to sharestuff.org.uk')

    def test_02_registration(self):
        # regex to scrape an activation key out of an activation email body
        activation_key_re = re.compile(r'/([a-f0-9]{40})/')

        client = Client()
        response = client.get('/accounts/register/')
        self.assertContains(response, 'Please complete the form below to register')

        response = client.post('/accounts/register/', {})
        self.assertContains(response, 'This field is required')

        response = client.post('/accounts/register/', {'username':'testuser',
                                                       'email':'test@test.com',
                                                       'password1':'password',
                                                       'password2':'password',},
                                redirect=True)

        # Check we got an email
        assert len(mail.outbox) == 1

        # Check it contains something that looks like an activation key
        matches = activation_key_re.search(mail.outbox[0].body)
        response = client.get('/accounts/activate/%s/' % matches.group(1))
        self.assertContains(response, 'We have activated your account')

        
    def test_03_login(self):
        self.test_02_registration()
        client = Client()
        response = client.get('/accounts/login/')
        self.assertContains(response, 'Please enter your username and password')

        response = client.post('/accounts/login/', {'username':'testuser'})
        self.assertContains(response, 'This field is required')

        response = client.post('/accounts/login/', {'username':'testuser',
                                                    'password':'password'},
                               follow=True)

        self.assertContains(response, "testuser's profile")
#        assert False




