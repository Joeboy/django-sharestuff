from django.core.management.base import NoArgsCommand, CommandError

def bootstrap():
    """
    Create mock users and offers for testing etc
    """
    from django.contrib.auth.models import User
    from userprofile.models import UserProfile
    from offers.models import Offer

    user = User.objects.create(username="Joeboy",
                               email="joeboy@test.com",
                               is_active=True,
                               is_staff=True,
                               is_superuser=True)
    user.set_password('password')
    user.save()

    userprofile = UserProfile.objects.create(user=user,)

    offer1 = Offer.objects.create(donor=userprofile,
                                  title="Ironing Board",
                                  description="This is an awesome board. 18m high, with spittoon and wings.",)

    offer1 = Offer.objects.create(donor=userprofile,
                                  title="Marrows",
                                  description="11 homegrown organic marrows. Like courgettes but bigger and not as good.",)

class Command(NoArgsCommand):
    help = 'Bootstrap the project database'

    def handle_noargs(self, *args, **options):
        bootstrap()
