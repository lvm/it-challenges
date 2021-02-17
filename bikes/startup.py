#!/usr/bin/env python
import os
import sys
import glob
import fnmatch
import argparse
from importlib import reload


def recursive_glob(rootdir='.', pattern='*.json', in_dir=''):
    files = []
    for root, dirnames, filenames in os.walk(rootdir):
        files.extend(glob.glob(root + "/" + pattern))

    if in_dir:
        files = filter(lambda f: in_dir in f, files)

    return files


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", help="Initial setup",
                        action="store_true")
    parser.add_argument("--run", help="Basic runserver",
                        action="store_true")

    args = parser.parse_args()

    reload(sys)
    sys.path.append('/srv/bikes')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bikes.settings")

    import django
    django.setup()
    from django.core import management

    if args.init:
        from django.contrib.auth.models import User

        fixtures = recursive_glob("/srv/bikes", "*.json", 'fixtures')

        management.call_command('migrate')
        management.call_command('collectstatic', '--noinput')

        for fixture in fixtures:
            management.call_command('loaddata', fixture, commit=False)

        if not User.objects.filter(username='admin').count():
            User.objects.create_superuser(
                'admin',
                'admin@admin.admin',
                '123qweasd'
            )

    if args.run:
        management.call_command('runserver', '0.0.0.0:8000')
