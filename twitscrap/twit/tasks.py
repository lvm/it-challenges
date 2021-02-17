from models import TwitterUser
from django_q.tasks import (
    async, result
)
from django_q.brokers import get_broker
import twitter

broker = get_broker()


def create_user(username):
    # if the user already exists, then do nothing.
    # otherwise fetch the necessary data and create it. or not.
    try:
        TwitterUser.objects.get(username=username)
    except TwitterUser.DoesNotExist:
        user_data = twitter.get_userdata(username)
        if user_data.get('status'):
            TwitterUser.objects.create(**user_data.get('result'))


def import_user(username):
    action_id = async('twit.tasks.create_user', username)
    return result(action_id)
