import json
import requests

from pathlib import Path
from unittest import TestCase

# This would be a nice feature, instead of monkeypatch or making the actual request:
# from unittest.mock import Mock
# from unittest.mock import patch

from grait import RDAP
from grait.utils import str_to_ipv4
from grait.utils import RDAPService
from grait.utils import RDAPResponse


def json_load(path):
    ipv4_io = open(path, "r")
    dct = json.load(ipv4_io)
    ipv4_io.close()
    return dct


class RDAPTestCase(TestCase):
    IPV4_PATH = Path(__file__).parent / "test_data/iana_rdap_ipv4.json"
    APNIC_RESPONSE_PATH = Path(__file__).parent / "test_data/apnic_response.json"

    def setUp(self):
        self.rdap = RDAP()
        self.rdap._ipv4_json = json_load(self.IPV4_PATH)
        self.apnic = RDAPService(
            domain="https://rdap.apnic.net/",
            ranges=[
                "1.0.0.0/8",
                "14.0.0.0/8",
                "27.0.0.0/8",
                "36.0.0.0/8",
                "39.0.0.0/8",
                "42.0.0.0/8",
                "43.0.0.0/8",
                "49.0.0.0/8",
                "58.0.0.0/8",
                "59.0.0.0/8",
                "60.0.0.0/8",
                "61.0.0.0/8",
                "101.0.0.0/8",
                "103.0.0.0/8",
                "106.0.0.0/8",
                "110.0.0.0/8",
                "111.0.0.0/8",
                "112.0.0.0/8",
                "113.0.0.0/8",
                "114.0.0.0/8",
                "115.0.0.0/8",
                "116.0.0.0/8",
                "117.0.0.0/8",
                "118.0.0.0/8",
                "119.0.0.0/8",
                "120.0.0.0/8",
                "121.0.0.0/8",
                "122.0.0.0/8",
                "123.0.0.0/8",
                "124.0.0.0/8",
                "125.0.0.0/8",
                "126.0.0.0/8",
                "133.0.0.0/8",
                "150.0.0.0/8",
                "153.0.0.0/8",
                "163.0.0.0/8",
                "171.0.0.0/8",
                "175.0.0.0/8",
                "180.0.0.0/8",
                "182.0.0.0/8",
                "183.0.0.0/8",
                "202.0.0.0/8",
                "203.0.0.0/8",
                "210.0.0.0/8",
                "211.0.0.0/8",
                "218.0.0.0/8",
                "219.0.0.0/8",
                "220.0.0.0/8",
                "221.0.0.0/8",
                "222.0.0.0/8",
                "223.0.0.0/8",
            ],
            publication="2019-06-07T19:00:02Z",
        )
        self.apnic_response = RDAPResponse(data=json_load(self.APNIC_RESPONSE_PATH))

    def test_get_service(self):
        self.assertEqual(self.rdap.get_service("https://rdap.apnic.net/"), self.apnic)

    def test_find_service(self):
        self.assertEqual(self.rdap.find_service("36"), self.apnic)

    def test_lookup(self):
        self.assertEqual(self.rdap.lookup("112.2.3.4"), self.apnic_response)

    def test_lookup_serialized(self):
        self.assertEqual(
            self.rdap.lookup_serialized("112.2.3.4"),
            json.dumps(self.apnic_response.asdict()),
        )
