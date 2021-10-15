#!/usr/bin/env python3

import json
import functools

import requests

from typing import List
from typing import Type
from typing import Literal
from typing import Optional

from .utils import get_octet
from .utils import RDAPService
from .utils import RDAPResponse


class RDAP:
    """RDAP.

    Queries the IANA for IPv4 RDAP Services and builds a dict of RDAPServices.
    Each one of these services can query their servers for an IP RDAP info.

    Arguments:
        ...

    Returns:
        [RDAP]: An RDAP objects.
        Provides many methods:

    RDAP.get_services: Returns `RDAPService`s.
    RDAP.find_service: Returns a `RDAPService` based on the first octet.
    RDAP.lookup: Lookups an IP RDAP info.
    RDAP.lookup_serialized: Serialized version of RDAP.lookup.
    RDAP.batch_lookup: Batch version of RDAP.lookup
    RDAP.batch_lookup_serialized: Batch version of RDAP.lookup_serialized
    """

    IPV4_ALLOC = "https://data.iana.org/rdap/ipv4.json"

    def __init__(self) -> Literal[None]:
        self._ipv4_json = None
        self._get_ipv4_json()

    @functools.lru_cache()
    def _get_ipv4_json(self) -> dict:
        """Returns iana.org IPv4 RDAP info.

        Arguments:
                ...
        Returns:
                Response(...)
        """
        if self._ipv4_json:
            return self._ipv4_json

        response = requests.get(self.IPV4_ALLOC)
        if response.ok:
            self._ipv4_json = response.json()

    def _get_services(self) -> dict:
        """Requests the IANA for RDAP Services and their ranges.

        Arguments:
                ...
        Returns:
                {service: RDAPService(...), ...}
        """
        services = {}
        ipv4_json = self._ipv4_json
        publication_date = ipv4_json.get("publication")
        for ranges, service in ipv4_json.get("services"):
            service = [reg for reg in service if reg.startswith("https://")]
            service = service.pop(0)
            services.update(
                {
                    service: RDAPService(
                        domain=service,
                        ranges=ranges,
                        publication=publication_date,
                    )
                }
            )

        return services

    def get_services(self) -> dict:
        """Returns the (cached) response of whatever IANA responded.

        Arguments:
                ...
        Returns:
                {service: RDAPService(...), ...}
        """
        return self._get_services()

    def get_service(self, domain: str) -> Optional[Type["RDAPService"]]:
        """Returns a single Service based on its domain.

        Arguments:
                domain: str -> https://an.rdap.tld/service/
        Returns:
                RDAPService(...)
        """
        return self._get_services().get(domain, None)

    def find_service(self, octet: str) -> Optional[Type["RDAPService"]]:
        """Returns a single Service based if the first octet matches with any of its first_octets.

        Arguments:
                octet: str -> 190
        Returns:
                RDAPService(...)
        """
        services = [
            service
            for domain, service in self.get_services().items()
            if octet in service.first_octets
        ]
        if services:
            return services.pop(0)

    def _query_service(
        self, service: Type["RDAPService"], ip_addr: str
    ) -> Optional[Type["RDAPResponse"]]:
        """Returns the actual RDAP request to get an IP RDAP info.

        Arguments:
                service: RDAPService -> RDAPService(...)
                ip_addr: str -> 190.2.3.4
        Returns:
                RDAPResponse(...)
        """
        return service.query_ip(ip_addr)

    def lookup(self, ip_addr: str) -> Optional[Type["RDAPResponse"]]:
        """Finds the correct RDAPService and will perform a RDAP request with RDAP._query_service.

        Arguments:
                ip_addr: str -> 190.2.3.4
        Returns:
                RDAPResponse(...)
        """
        octet = get_octet(ip_addr)
        service = self.find_service(octet)
        if service:
            return self._query_service(service, ip_addr)

    def lookup_serialized(self, ip_addr: str) -> str:
        """Serialized version of RDAP.lookup

        Arguments:
                ip_addr: str -> 190.2.3.4
        Returns:
                {...}
        """
        who_ = self.lookup(ip_addr).asdict()
        return json.dumps(who_)

    def batch_lookup(self, ip_addresses: list) -> List[Optional[Type["RDAPResponse"]]]:
        """Batch version of RDAP.lookup.

        Arguments:
                ip_addresses: List[str] -> [190.2.3.4, 200.4.5.5,...]
        Returns:
                [RDAPResponse(...), ...]
        """
        return [self.lookup(ip_addr) for ip_addr in ip_addresses]

    def batch_lookup_serialized(self, ip_addresses: list) -> str:
        """Batch version of RDAP.lookup_serialized.

        Arguments:
                ip_addresses: List[str] -> [190.2.3.4, 200.4.5.5,...]
        Returns:
                [{...}, ...]
        """
        serialized = {}
        lookups = self.batch_lookup(ip_addresses)
        if lookups:
            serialized = [lu.asdict() for lu in lookups]
        return json.dumps(serialized)
