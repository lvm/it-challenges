#!/usr/bin/env python

from fabric.api import local

ADMIN_USER = "admin"
ADMIN_EMAIL = "admin@admin.admin"
ADMIN_PW = "123qweasd"


def manage_py(action):
    if action:
        local('python manage.py {}'.format(action))


def q_cluster():
    manage_py('qcluster')


def manage_createsuperuser():
    manage_py('createsuperuser --no-input --username {user} --email {email}'
              .format(user=ADMIN_USER, email=ADMIN_EMAIL)
    )
    local('python superuser-pw.py {}'.format(ADMIN_PW))


def init_django_local():
    print "Running migrations"
    manage_py('makemigrations')
    manage_py('migrate')

    print "Creating the admin"
    manage_createsuperuser()


def deploy_local():
    init_django_local()
