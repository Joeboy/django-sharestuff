from registration.signals import user_activated

from userprofile.models import UserProfile
def create_userprofile(sender, **kwargs):
    userprofile = UserProfile.objects.create(user=kwargs.get('user'))

user_activated.connect(create_userprofile, dispatch_uid="asdf")
