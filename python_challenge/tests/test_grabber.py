import json

from pathlib import Path
from unittest import TestCase

from grait import IPGrabber
from grait.utils import IPobject
from grait.utils import str_to_ipv4

class IPGrabberTestCase(TestCase):
    IPFILE_PATH = Path(__file__).parent / "test_data/grabber_test.txt"

    def setUp(self):
        self.ipg = IPGrabber(self.IPFILE_PATH)
        self.ip_list = [
            "82.229.199.149",
            "206.134.207.195",
            "124.70.169.32",
            "212.74.86.233",
            "0.175.79.88",
            "4.130.36.19",
            "15.190.43.42",
            "212.219.78.78",
        ]
        ipobject_list = []
        for ip_ in self.ip_list:
            ip = str_to_ipv4(ip_)
            ipobject_list.append (
                IPobject(
                    **{"ip": ip_, "object": ip, "is_valid": ip.is_global}
                )
            )
        self.result = tuple(ipobject_list)
        self.result_serialized = json.dumps([row.asdict() for row in self.result])


    def test_grab_ips(self):
        "test ip regex"
        text = "Lorem ipsum dolor sit amet, 124.70.169.32 adipiscing elit. "
        self.assertEqual(self.ipg._grab_ips(text), ["124.70.169.32",])

    def test_result(self):
        "test results"
        self.assertEqual(self.result, self.ipg.get_result())

    def test_result_serialized(self):
        "test results serialized"
        self.assertEqual(self.result_serialized, self.ipg.get_result_serialized())
