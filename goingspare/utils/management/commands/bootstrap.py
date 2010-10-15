from django.core.management.base import NoArgsCommand
from django.core.management import call_command

class Command(NoArgsCommand):
    """
    Do some stuff that saves a bit of time when developing
    """

    def handle_noargs(self, **options):
        from django.contrib.auth.models import User
        from userprofile.models import UserProfile
        from offers.models import LocalOffer

        call_command('syncdb', interactive=False)

        u = User.objects.create(username='testuser',
                                email = 'test@example.com',
                                )
        u.set_password('password')
        u.is_superuser = True
        u.is_staff = True
        u.save()

        up = UserProfile.objects.create(user=u)

        offer1 = LocalOffer.objects.create(donor=up,
                                      title="Ironing Board",
                                      description="This is an awesome board. 18m high, with spittoon and wings.",)

        offer2 = LocalOffer.objects.create(donor=up,
                                      title="Marrows",
                                      description="11 homegrown organic marrows. Like courgettes but bigger and not as good.",)

        offer3 = LocalOffer.objects.create(donor=up,
                                           title="Woman's bicycle",
                                           description="Raleigh woman's bike in reasonable condition but needs some attention. 18\" frame.")

