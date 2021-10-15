#!/usr/bin/env python3

import csv
import json
import ipaddress
import functools

from pathlib import Path

from typing import Any
from typing import List
from typing import Type
from typing import Union
from typing import Literal
from typing import Optional

from world_class import World

# This module is not really needed since we can get a Country from World()
# from world_class import Country

from .utils import IPv4
from .utils import IPCountry
from .utils import get_octet


class GeoIP:
    """GeoIP.

    Parses a Geo Legacy IP Range/Country CSV file and tries to geo-locate an IPv4.

    Arguments:
        geofile (str, Path): A Path obj or a string that represents a path file.

    Returns:
        [GeoIP]: A GeoIP objects.
        Provides many methods:
    GeoIP.get_country: Returns a Country
    GeoIP.get_country_range: Returns a list of (first, last) pairs of IPv4Networks for a Country.
    GeoIP.in_country_range: Returns a bool based on if an IPv4 is in a IPv4Network.
    GeoIP.locate: Returns an IPCountry (that is: an IP + a Country) based on an IP.
    GeoIP.locate_serialized: Serialized version of GeoIP.locate
    GeoIP.batch_locate: Batch version of GeoIP.locate
    GeoIP.batch_locate_serialized: Batch version of GeoIP.locate_serialized
    """

    _country_cache = {}
    _octet_cache = {}

    def __init__(self, geofile: Union[str, Path]) -> Literal[None]:
        self.geofile = geofile
        if not hasattr(self.geofile, "exists"):
            self.geofile = Path(self.geofile)
        assert self.geofile.exists(), FileNotFoundError(
            "Geo Legacy file doesn't exists!"
        )
        self._parse

    def _update_cache(self, cc: str, first_ip: str, last_ip: str) -> Literal[None]:
        """
        GeoIP contains two caches:
        * _country_cache = {COUNTRY_CODE: (ranges), ...}
        * _octet_cache = {IP_FIRST_OCTET: [COUNTRY_CODES, ...], ...}

        This `private` method, updates both.

        Arguments:
                cc: str -> Country Code
                first_ip: str -> 1.2.3.0
                last_ip: str -> 1.2.3.255
        Returns:
                ...
        """
        first_oct = get_octet(first_ip)
        last_oct = get_octet(last_ip)
        octets = [first_oct, last_oct] if first_oct != last_oct else [first_oct]
        # First octet_cache
        for octet in octets:
            if octet not in list(GeoIP._octet_cache.keys()):
                GeoIP._octet_cache.update({octet: set([cc])})
            else:
                GeoIP._octet_cache[octet].add(cc)
        # Then the country_cache
        if cc not in list(GeoIP._country_cache.keys()):
            GeoIP._country_cache.update({cc: [(first_ip, last_ip)]})
        else:
            GeoIP._country_cache[cc].append((first_ip, last_ip))
        # that's all.

    def _query_cache(self, which: str, key: Any) -> Any:
        """A private generic methods to query both caches.

        Arguments:
                which: str -> "octet"
                key: Any -> 190
        Returns:
                Any object cached based on its `key`.
        """
        cache_ = getattr(GeoIP, f"_{which}_cache")
        return cache_.get(key, None)

    def _read(self) -> Literal[None]:
        """Reads a Geo Legacy IP CSV.

        Arguments:
                ...
        Returns:
                Yields (CSV) lines.
        """
        with open(self.geofile, "r") as geo:
            for row in csv.reader(geo, delimiter=","):
                yield row

    def _process(self, row: list) -> dict:
        """A `private` method to process csv rows and update GeoIP cache.

        Arguments:
                row: list -> ["1.2.3.4", "1.2.3.255", "123123123", "123123125", "AR", "Argentina"]
        Returns:
                ...
        """
        first_ip, last_ip, _1, _2, country_code, _3 = row
        self._update_cache(country_code, first_ip, last_ip)

    @functools.cached_property
    def _parse(self):
        """A `private` method to parse the CSV file.

        Arguments:
                ...
        Returns:
                ...
        """
        for row in self._read():
            try:
                assert (
                    len(row) == 6
                ), "Malformed Geo Legacy file, there are missing columns!"
            except Exception as e:
                print(f"[-] ERR: {e}")
            else:
                self._process(row)

    def get_country(self, country_code: str) -> dict:
        """Returns a Country from a country code.

        Arguments:
                country_code -> "AR"
        Returns:
                Country(...)
        """
        return World().find_by_code(value=country_code)

    def get_country_range(
        self, country_code: str, first_octet: Optional[Union[int, str]] = None
    ) -> list:
        """Returns a list of (first, last) pairs of IPv4Networks for a Country.

        Arguments:
                country_code -> "AR"
                first_octet:int,str,Optional -> 190
        Returns:
                [(first_ip, last_ip), (another_first_ip, another_last_ip), ...]
        """
        country_ranges = self._query_cache("country", country_code)
        if first_octet:
            first_octet = f"{first_octet}."
            country_ranges = [
                (f, l)
                for f, l in country_ranges
                if f.startswith(first_octet) or l.startswith(first_octet)
            ]

        return country_ranges

    def in_country_range(
        self, country_ranges: list, ip_addr: Union[str, IPv4, ipaddress.IPv4Address]
    ) -> bool:
        """Returns a bool based on if an IPv4 is in a IPv4Network.

        Arguments:
                country_ranges -> [(first_ip, last_ip), (another_first_ip, another_last_ip), ...]
                ip_addr:str,IPv4,ipaddress.IPv4Address -> 190.10.22.63
        Returns:
                bool
        """
        if isinstance(ip_addr, ipaddress.IPv4Address):
            ip_addr = ip_addr.compressed

        if isinstance(ip_addr, str):
            ip_addr = IPv4(ip_addr)

        for first, last in country_ranges:
            first, last = [IPv4(_) for _ in [first, last]]
            for net in ipaddress.summarize_address_range(first, last):
                if ip_addr in net:
                    return True

        return False

    def locate(
        self, ip_addr: Union[str, IPv4, ipaddress.IPv4Address]
    ) -> Optional[Type["IPCountry"]]:
        """Returns an IPCountry (that is: an IP + a Country) based on an IP.

        Arguments:
                ip_addr:str,IPv4,ipaddress.IPv4Address -> 190.10.22.63
        Returns:
                IPCountry(...)
        """
        if isinstance(ip_addr, (IPv4, ipaddress.IPv4Address)):
            ip_addr = ip_addr.compressed

        f_octet = get_octet(ip_addr)
        country_codes = self._query_cache("octet", f_octet)
        if country_codes:
            for cc in country_codes:
                country_range = self.get_country_range(cc, f_octet)
                if self.in_country_range(country_range, ip_addr):
                    return IPCountry(ip=ip_addr, country=self.get_country(cc))

    def locate_serialized(
        self, ip_addr: Union[str, IPv4, ipaddress.IPv4Address]
    ) -> dict:
        """Serialized version of GeoIP.locate

        Arguments:
                ip_addr:str,IPv4,ipaddress.IPv4Address -> 190.10.22.63
        Returns:
                {...}
        """
        serialized = {}
        located = self.locate(ip_addr)
        if located:
            serialized = located.asdict()
        return json.dumps(serialized)

    def batch_locate(self, ip_addresses: list) -> Optional[List[Type["IPCountry"]]]:
        """Returns a list of IPCountry (that is: an IP + a Country) based on a list of IPs.

        Arguments:
                ip_addresses:List[str,IPv4,ipaddress.IPv4Address] -> [1.2.3.4, 190.10.22.63, ...]
        Returns:
                [IPCountry(...), ...]
        """
        return [self.locate(ip_addr) for ip_addr in ip_addresses]

    def batch_locate_serialized(self, ip_addresses: list) -> str:
        """Batch version of GeoIP.locate_serialized

        Arguments:
                ip_addresses:List[str,IPv4,ipaddress.IPv4Address] -> [1.2.3.4, 190.10.22.63, ...]
        Returns:
                [{...}, ...]
        """
        serialized = {}
        located = self.batch_locate(ip_addresses)
        if located:
            serialized = [loc.asdict() for loc in located if loc]
        return json.dumps(serialized)
