#!/usr/bin/env python3

import re
import requests
import ipaddress
import functools

from typing import List
from typing import Type
from typing import Union
from typing import Literal
from typing import Optional
from typing import NoReturn

from dataclasses import field
from dataclasses import asdict
from dataclasses import InitVar
from dataclasses import dataclass

from world_class import World
from world_class import Country

from requests import Response

UNKNOWN_COUNTRY = World().find_by_code(value="xx")


class IPv4(ipaddress.IPv4Address):
    """IPv4.

    Inherits from `ipaddress.IPv4Address` and adds a "magic" `__dict__` method.

    Arguments:
        address: str -> "N.N.N.N"

    Returns:
        [IPv4]: Returns an IPv4 object.
    """

    @property
    def __dict__(self) -> dict:
        return {
            attr: getattr(self, attr)
            for attr in [
                "compressed",
                "exploded",
                "is_global",
                "is_link_local",
                "is_loopback",
                "is_multicast",
                "is_private",
                "is_reserved",
                "is_unspecified",
                "max_prefixlen",
                "reverse_pointer",
                "version",
                # "packed",
                # this one is left behind to make things simpler,
                # as not always ip.packed.decode("utf8") works as expected
                # and it's not really necessary for this particular scenario.
            ]
        }


@dataclass
class Base:
    """Base.

    A Base dataclass that provies `_asdict` methods.

    Arguments:
        ...

    Returns:
        [Base]: A Base class.
    """

    def _asdict(self) -> dict:
        """Returns a dict based on the dataclass fields/contents.
        Ideally to be used in conjunction with `json.dumps`

        Arguments:
                ...
        Returns:
                {...}
        """
        self_dict = asdict(self)
        for k, v in self_dict.items():
            if hasattr(v, "__dict__"):
                self_dict.update({k: v.__dict__})

        return self_dict

    def asdict(self) -> dict:
        """See Base._asdict()

        Arguments:
                ...
        Returns:
                {...}
        """
        return self._asdict()


@dataclass
class IPobject(Base):
    """IPobject.

    Works as a friendly interface to interact with the results from IPGrabber.

    Arguments:
        ip: str -> "N.N.N.N"
        object: IPv4 -> IPv4("N.N.N.N")
        is_valid: bool -> True

    Returns:
        [IPobject]: Returns an IP dataclass, which provides an IP.asdict() method
        to get a JSON-serializable `dict`.
    """

    ip: str
    object: ipaddress.IPv4Address
    is_valid: bool

    @property
    def _version(self) -> int:
        """Returns an IPv4Address.version attribute."""
        return self.object.version

    @property
    def version(self) -> int:
        """See IPObject._version."""
        return self._version


@dataclass
class IPCountry(Base):
    """IPobject.

    Works as a friendly interface to interact with a Country + IP addr.

    Arguments:
        ip: str -> "N.N.N.N"
        country: Country -> Country(...)

    Returns:
        [IPCountry]: Returns an IPCountry dataclass.
    """

    ip: str
    country: Country


@dataclass
class RDAPResponse(Base):
    """RDAPResponse.

    A RDAP object is an object representation of a RDAP query JSON response.

    Arguments:
        data: dict -> {"handle": "...", "entities":..., ...}

    Returns:
        [RDAPResponse]: Returns a RDAPResponse dataclass.
    """

    data: InitVar[dict]
    handle: Optional[str] = field(default="")
    parent_handle: Optional[str] = field(default="")
    start_addr: Optional[str] = field(default="")
    end_addr: Optional[str] = field(default="")
    version: Optional[int] = field(default="")
    name: Optional[str] = field(default="")
    type: Optional[str] = field(default="")
    country: Optional[Country] = field(default=UNKNOWN_COUNTRY)
    entities: Optional[dict] = field(default=dict)
    remarks: Optional[dict] = field(default=dict)
    links: Optional[List[dict]] = field(default=list)
    events: Optional[dict] = field(default=dict)
    conformance: Optional[list] = field(default=list)
    notices: Optional[List[dict]] = field(default=list)
    port43: Optional[str] = field(default="")

    def __post_init__(self, data: dict) -> Literal[None]:
        self.handle = data.get("handle", "")
        self.parent_handle = data.get("parentHandle", "")
        self.start_addr = data.get("startAddress", "")
        self.end_addr = data.get("endAddress", "")
        self.version = self._parse_version(data.get("ipVersion", ""))
        self.name = data.get("name", "")
        self.type = data.get("type", "")
        self.entities = self._parse_entities(data.get("entities", []))
        self.country = self._parse_country(data.get("country", "XX"))
        self.remarks = data.get("remarks", {})
        self.links = data.get("links", {})
        self.events = data.get("events", {})
        self.conformance = data.get("rdapConformance", [])
        self.notices = data.get("notices", [])
        self.port43 = data.get("port43", "")

    def _parse_version(self, version: str) -> int:
        """Returns the IP version as integer. Either 4 or 6. Most likely 4.
        See: https://xkcd.com/221/

        Arguments:
                ...
        Returns:
                dict -> {ip: IP object, ...}
        """
        return int(re.sub("v", "", version))

    def _parse_country_code_from_entities(self, entities: list) -> str:
        """Returns a Country Code, taken from the VCard Address attribute.
        Used as a backup plan when RDAP Services don't have a "country" attr.

        Arguments:
                entities: list -> [{rdap-entity-data}, ...]
        Returns:
                "AR"
        """
        for handle, entities in self.entities.items():
            if "registrant" in entities.get("roles", []):
                for data in entities.get("vcard", []):
                    if "adr" in list(data.keys()):
                        address = data.get("text")
                        if isinstance(address, list):
                            pobox, apt, street, city, region, postal, country = address
                            return country

        return ""

    def _parse_country(self, country_code: str, _retry: bool = True) -> Type["Country"]:
        """Returns a Country. If no country can be found, will call
        RDAPResponse._parse_country_code_from_entities and try to get a Country Code.
        If everything fails, will return an "Unknown Country".

        Arguments:
                country_code: str -> "AR"
                _retry: bool, Optional -> False
        Returns:
                Country(...)
        """
        country = World().find_by_code(value=country_code)
        if country == UNKNOWN_COUNTRY and _retry:
            country_code = self._parse_country_code_from_entities(self.entities)
            if country_code:
                return self._parse_country(country_code, False)
            else:
                return UNKNOWN_COUNTRY
        else:
            return country

    def _parse_vcard(self, vcard: list) -> list:
        """Returns a list of dicts with the VCard attributes.

        Arguments:
                vcard: list -> ["vcard", [...]]
        Returns:
                [{...}, {...}, ...]
        """
        vcard_ = []

        def pairs_to_dict(pairs):
            pairs_ = iter(pairs)
            return dict(zip(pairs_, pairs_))

        _, vdata = vcard
        for pairs in vdata:
            pairs_dct = pairs_to_dict(pairs)
            vcard_.append(pairs_dct)

        return vcard_

    def _parse_entities(self, entities: list) -> dict:
        """Returns a dict with the Entities parsed (non-recursive).

        Arguments:
                entities: list -> [...]
        Returns:
                {entity-name: {...}, ...}
        """
        entities_ = {}
        for ent in entities:
            handle = ent.get("handle", "")
            roles = ent.get("roles", [])
            vcard = ent.get("vcardArray", [])

            if handle:
                entities_.update({handle: {}})
                if roles:
                    entities_[handle]["roles"] = roles
                if vcard:
                    entities_[handle]["vcard"] = self._parse_vcard(vcard)

        return entities_


@dataclass
class RDAPService(Base):
    """RDAPService.

    RDAP bootstrap file for IPv4 address allocations.

    Arguments:
        domain: List[str] -> "https://rdap.db.ripe.net/"
        ranges: List[Union[str, ipaddress.IPv4Network]] -> ["2.0.0.0/8", "5.0.0.0/8", "25.0.0.0/8"]
        publication: str -> "2019-06-07T19:00:02Z"

    Returns:
        [RDAPService]: Returns an RDAPService dataclass.
    """

    domain: str
    ranges: List[Union[str, ipaddress.IPv4Network]]
    publication: str

    @functools.cached_property
    def addr_ranges(self) -> dict:
        """Returns a dict with the RDAPService ranges that can be queried."""
        self._addr_range = {}
        for range_ in self.ranges:
            octet = get_octet(range_)
            if octet not in list(self._addr_range.keys()):
                self._addr_range.update({octet: ipaddress.IPv4Network(range_)})

        return self._addr_range

    @functools.cached_property
    def first_octets(self) -> list:
        """Returns a list of octets for this RDAPService."""
        return [get_octet(range_) for range_ in self.ranges]

    def get_query_url(self, ip_addr: str) -> str:
        """Returns a RDAP Service url.

        Arguments:
                ip_addr: str -> 1.2.3.4
        Returns:
                https://rdap.service.tld/ip/1.2.3.4
        """
        domain = self.domain.strip("/")
        return f"{domain}/ip/{ip_addr}"

    def query_ip(self, ip_addr: str) -> Optional[Type["RDAPResponse"]]:
        """Returns a RDAPResponse

        Arguments:
                ip_addr: str -> 1.2.3.4
        Returns:
                RDAPResponse(...)
        """
        response = http_get(self.get_query_url(ip_addr))
        if response.ok:
            return RDAPResponse(data=response.json())


def str_to_ipv4(ip_addr: str) -> Union[ipaddress.IPv4Address, IPv4, NoReturn]:
    """Returns an IPv4 object

    Arguments:
        ip_addr: str -> 1.2.3.5
    Returns:
        IPv4(...)
    """
    try:
        ipv4 = IPv4(ip_addr)
    except Exception as e:
        raise e
    else:
        return ipv4


def get_octet(ip_addr: str, idx: int = 0) -> str:
    """Returns an octet (0 to 255)"

    Arguments:
        ip_addr: str -> 1.2.3.4
        idx: int -> 0
    Returns:
        123
    """
    return str(ip_addr.split(".")[idx])


@functools.lru_cache()
def http_get(url: str) -> Type["Response"]:
    """Returns a HTTP Response

    Arguments:
        url: str -> https://domain.tld/
    Returns:
        Response(...)
    """
    return requests.get(url)
