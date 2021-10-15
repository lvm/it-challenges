import json
import random

from pathlib import Path
from unittest import TestCase

from world_class import Country
from world_class import World

from grait import GeoIP
from grait.utils import IPv4
from grait.utils import IPCountry
from grait.utils import get_octet


def get_country(cc: str) -> Country:
    return World().find_by_code(value=cc)


class GeoIPTestCase(TestCase):
    GEOCSV_PATH = Path(__file__).parent / "test_data/geoipwhois_test.csv"

    def setUp(self):
        self.geo = GeoIP(self.GEOCSV_PATH)
        self.cc = ["JP", "IN", "CN", "MY", "AU", "TH", "KR", "DE", "AU"]
        self.cc_oct = {cc: "2" if cc == "DE" else "1" for cc in self.cc}
        self.countries = {cc: get_country(cc) for cc in self.cc}
        self.country_ranges = {
            cc: self.geo.get_country_range(cc, self.cc_oct.get(cc)) for cc in self.cc
        }
        self.country_ips = {
            "DE": "2.16.6.23",
            "KR": "1.16.1.2",
            "JP": "1.21.3.4"
        }

    def test_get_country(self):
        "test geoip.get_country"
        cc = random.choice(self.cc)
        self.assertEqual(self.countries.get(cc), self.geo.get_country(cc))

    def test_get_country_range(self):
        "test geoip.get_country"
        cc = random.choice(self.cc)
        octet = self.cc_oct.get(cc)
        self.assertEqual(self.country_ranges.get(cc), self.geo.get_country_range(cc, octet))

    def test_in_country_range(self):
        "test geoip.get_country"
        cc = random.choice([cc for cc in list(self.country_ips.keys())])
        octet = self.cc_oct.get(cc)
        ip = self.country_ips.get(cc)
        country_ranges = self.geo.get_country_range(cc, octet)
        self.assertEqual(self.geo.in_country_range(country_ranges, ip), True)

    def test_locate(self):
        "test geoip.get_country"
        cc = random.choice([cc for cc in list(self.country_ips.keys())])
        ip = self.country_ips.get(cc)
        country = self.countries.get(cc)
        ipcountry = IPCountry(ip, country)
        self.assertEqual(ipcountry, self.geo.locate(ip))
