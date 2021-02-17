import json
from django.test import (
    TestCase, Client
)
from models import TwitterUser

users_to_test = ['automagico', 'badreligion', 'tidalcycles', '_why', '_']

class TwitterUserTestCase(TestCase):

    def test_post_users(self):
        c = Client()
        for user in users_to_test:
            resp = c.post('/users/{}'.format(user))
            self.assertEqual(resp.json().get('message'), "processing request")
