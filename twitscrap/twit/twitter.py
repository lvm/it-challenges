#!/usr/bin/env python

"""
The reason why I'm scrapping data this way is because Twitter wants me to
add my phone # to create an App. nope.jpeg
"""

import json
import requests
from bs4 import BeautifulSoup as bs

TWITTER_URL = "https://twitter.com/{}"
DEBUG = False

def get_userdata(username):
    status = False
    ret = {'username': username,
           'description': "",
           'followers': 0,
           'avatar': "",
    }

    # testing purposes
    if not DEBUG:
        r = requests.get(TWITTER_URL.format(username))
        content = r.text
    else:
        # the content of `twitter.html` (not provided)
        # is simply the result of:
        # $ wget https://twitter.com/somebody > twitter.html
        f = open('./twitter.html', 'r')
        content = '\n'.join(f.readlines())
        f.close()

    soup = bs(content, 'html.parser')
    data = soup.find_all('input', class_='json-data')

    # Basically, I'll search for an input with the json-data class
    # provided by Twitter in the profiles, so I don't really need
    # to scrap all the HTML :-)
    if data:
        json_data = json.loads(data[0].get('value'))
        user_data = json_data.get('profile_user')

        ret.update({'description': user_data.get('description'),
                    'followers': user_data.get('followers_count'),
                    'avatar': user_data.get('profile_image_url_https')})
        status = True

    # this way I can later know if I should add the user or not.
    return {'result': ret, 'status': status}


if __name__ == "__main__":
    # this should fail
    print get_userdata('wqe9dq8whd9q8hautomagico')

    # this should'nt
    print get_userdata('automagico')
