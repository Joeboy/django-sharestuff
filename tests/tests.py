from django.test import TestCase
from django.test.client import Client

class GlobalTest(TestCase):

    def test_homepage(self):
        client = Client()
        response = client.get('/')
        self.assertContains(response, 'Welcome to sharestuff.org.uk')
