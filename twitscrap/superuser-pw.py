#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "twitscrap.settings")

    import django
    django.setup()
    from django.contrib.auth.models import User

    if len(sys.argv):
        admin = User.objects.get(username='admin')
        admin.set_password(sys.argv[1])
        admin.save()
