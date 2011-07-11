from goingspare.utils import render_to_response_context
from django.db import transaction

@transaction.commit_on_success
def index(request):
    userprofile = request.user.get_profile()
    notifications = request.user.get_profile().notification_set.all()
    notifications.filter(read=False).update(read=True)
    return render_to_response_context(request,
                                          'notifications/index.html',
                                          {'notifications': notifications})
