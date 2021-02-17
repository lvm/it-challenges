#!/usr/bin/env python3

DEPENDENCIES_OK = False
import sys
try:
    import requests_html
    from PIL import (
        Image,
        ImageDraw,
        ImageFont
    )
    import piexif
    import piexif.helper
    DEPENDENCIES_OK = True
except ImportError as error:
    print ("""# Install dependencies:
# $ python3 app.py | grep -v "#" | xargs pip install -U
requests\nrequests_html\nPillow\npiexif""")
    sys.exit(1)

import re
import tempfile
from io import BytesIO
from pathlib import Path


def level_3(path: str) -> str:
    return "http://www.proveyourworth.net/level3/{}".format(path)


def start(session: type) -> str:
    """
    Will `start` by looking for the "hash".
    I have to admit that first I thought it was something like
    `Robert'); show tables;`. Luckily it was easier.

    :param Session requests_html.Session()
    :return Text (statefulhash)
    :rtype str
    """
    url = level_3("start")
    r = session.get(url)
    st_hash = ""

    if r.ok:
        print ("/start", r.headers)
        st_hash = r.html.find("[name='statefulhash']", first=True)
        st_hash = st_hash.attrs.get('value')

    return st_hash


def activate(session: type, st_hash: str) -> str:
    """
    Now I'll continue by taking a look to the headers, as the
    HTML source suggested :-)

    :param Session requests_html.Session(), Text statefulhash
    :return Url
    :rtype str
    """
    url = level_3("activate?statefulhash={}".format(st_hash))
    r = session.get(url)
    payload_url = ""

    if r.ok:
        print ("/activate", r.headers)
        payload_url = r.headers.get('X-Payload-URL')

    return payload_url


def payload(session: type, url: str) -> tuple:
    """
    Now that I got the URL, I'll find out what this
    `payload` is about and where I need to send it.

    :param Session requests_html.Session(), Text url
    :return Tuple[str, str]
    :rtype [Url, Path]
    """
    r = session.get(url)
    path = Path(tempfile.mkdtemp(prefix="pyw_"))
    reaper_url = ""
    if r.ok:
        reaper_url = r.headers.get('X-Post-Back-To')
        filename = re.sub(r"inline; filename=(.*)", r"\1",
                          r.headers.get('Content-Disposition'))
        img = Image.open(BytesIO(r.content))
        path = path / filename
        img.save(path)

    return reaper_url, path


def sign_payload(path: str, signature: str) -> str:
    """
    Let's "sign" the image with my-name+statefulhash.
    I wasn't sure if I had to add this 'signature' to the
    EXIF Tags but did it anyway.

    :param Path-like temporary-image-file, Text signature
    :return Path-like
    :rtype str
    """
    img = Image.open(open(path, 'rb'))

    font = ImageFont.truetype("mononoki-Regular", size=23)
    sign = ImageDraw.Draw(img)
    sign.text((23, 23), signature, font=font, fill="#f00")

    exif_comment = piexif.helper.UserComment.dump(signature)
    exif_data = {
        "Exif": {
            piexif.ExifIFD.UserComment: exif_comment
        }
    }
    img.save(path, exif=piexif.dump(exif_data))

    return path


def final_step(session: type, url: str,
               data: dict, files: dict) -> bool:
    """
    Now that I got everything, I'll just post it.
    It was a fun excercise :-)

    :param Session requests_html.Session(), Text url,
           dict {name, email, aboutme}, dict {resume, code, img}
    :return Bool
    :rtype bool
    """
    r = session.post(url, data=data, files=files)
    status = r.ok
    if status:
        # Just to see what the response is.
        print (r.headers)
        print (r.content)
        print (r.text)

    return status

if __name__ == "__main__":
    if DEPENDENCIES_OK:
        ABOUT_ME = """Hi this is the code to apply in PYW."""
        WHOAMI = {
            'name': 'Mauro ',
            'email': 'no@spam.tld',
            'aboutme': ABOUT_ME,
        }
        WHOAMI_FILES = {
            'resume': './cv.pdf',
            'image': '',
            'code': './app.py', # quine-ish.
        }

        session = requests_html.HTMLSession()
        st_hash = start(session)
        payload_url = activate(session, st_hash)
        reaper_url, payload_file = payload(session, payload_url)

        WHOAMI_FILES['image'] = payload_file
        sign_payload(WHOAMI_FILES['image'],
                     "{}\n{}".format(WHOAMI.get('name'), st_hash))

        for key in list(WHOAMI_FILES.keys()):
            WHOAMI_FILES[key] = open(WHOAMI_FILES.get(key), 'rb')

        res = final_step(session, reaper_url, WHOAMI, WHOAMI_FILES)
        sys.exit(0 if res else 1)
