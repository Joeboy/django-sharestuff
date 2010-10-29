from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.db import connection, transaction
from django.conf import settings

import re

class Command(NoArgsCommand):
    """
    Do some stuff that saves a bit of time when developing
    """

    @staticmethod
    def executescript(script_path):
        statements = re.compile(r";[ \t]*$", re.M)
        fp = open(script_path, 'U')
        output = []
        cursor = connection.cursor()
        for statement in statements.split(fp.read().decode(settings.FILE_CHARSET)):
            # Remove any comments from the file
            statement = re.sub(ur"--.*([\n\Z]|$)", "", statement)
            print statement
            if statement.strip():
#                output.append(statement + u";")
                cursor.execute(statement+u';')
        fp.close()

    def handle_noargs(self, **options):
        from django.contrib.auth.models import User
        from userprofile.models import UserProfile
        from offers.models import LocalOffer

        cursor = connection.cursor()
        call_command('syncdb', interactive=False)

        import os
        os.system('sudo su postgres -c "psql -d goingspare -U postgres -f /usr/share/postgresql/8.4/contrib/cube.sql; psql -d goingspare -U postgres -f /usr/share/postgresql/8.4/contrib/earthdistance.sql"')

        u = User.objects.create(username='testuser',
                                email = 'test@example.com',
                                )
        u.set_password('password')
        u.is_superuser = True
        u.is_staff = True
        u.save()
        up = UserProfile.objects.create(user=u)

        u2 = User.objects.create(username='testuser2',
                                 email='test2@example.com',)
        up2 = UserProfile.objects.create(user=u2)


        offer1 = LocalOffer.objects.create(donor=up,
                                      title="Ironing Board",
                                      description="This is an awesome board. 18m high, with spittoon and wings.",)

        offer2 = LocalOffer.objects.create(donor=up,
                                      title="Marrows",
                                      description="11 homegrown organic marrows. Like courgettes but bigger and not as good.",)

        offer3 = LocalOffer.objects.create(donor=up,
                                           title="Woman's bicycle",
                                           description="Raleigh woman's bike in reasonable condition but needs some attention. 18\" frame.")

