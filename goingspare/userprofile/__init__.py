from registration.signals import user_activated
from socialregistration.forms import UserForm
from userprofile.models import UserProfile

class SocialUserForm(UserForm):
    """
    A UserForm that also creates a UserProfile on saving
    """
    def save(self, *args, **kwargs):
        user = super(SocialUserForm, self).save(*args, **kwargs)
        UserProfile.objects.create(user=user)


def create_userprofile(sender, **kwargs):
    userprofile = UserProfile.objects.create(user=kwargs.get('user'))

user_activated.connect(create_userprofile, dispatch_uid="asdf")
