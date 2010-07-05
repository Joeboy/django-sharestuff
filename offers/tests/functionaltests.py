from django.test import TestCase
from django.test.client import Client
from bucket.management.commands.bootstrap import bootstrap

class OffersTest(TestCase):
    """
    Functional tests for offers app
    """

    def test_offers(self):
        bootstrap()
        client = Client()
        response = client.get('/~Joeboy/offers/')
        self.assertContains(response, "Joeboy's offers")
        self.assertContains(response, "Ironing Board")
