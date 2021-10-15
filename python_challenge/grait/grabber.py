#!/usr/bin/env python3

import re
import json
import ipaddress
import functools

from pathlib import Path
from typing import List
from typing import Union
from typing import Literal
from typing import Generator

from grait.utils import IPv4
from grait.utils import IPobject
from grait.utils import str_to_ipv4

class IPGrabber:
    """IPGrabber.

    Parses a plain text file and tries to grab every IPv4 address that can find.

    Arguments:
        ipfile (str, Path): A Path obj or a string that represents a path file.

    Returns:
        [IPGrabber]: An IPGrabber objects.
        Provides two (cached) methods: IPGrabber.get_result and (JSON) IPGrabber.get_result_serialized
    """

    # This regexp will catch anything from " 0.0.0.0 " to " 666.0.255.23 " (notice the \b's),
    # but this is fine, will validate later whatever it captured.
    # Something to note is that it wont capture "10.1", which is a valid IP but
    # not a public IP, so we do not care for it.
    # At least for this particular (challenge) case.
    IP_REGEX = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"

    def __init__(self, ipfile: Union[str, Path]) -> Literal[None]:
        self.ipfile = ipfile
        if not hasattr(self.ipfile, "exists"):
            self.ipfile = Path(self.ipfile)
        assert self.ipfile.exists(), FileNotFoundError("IP File doesn't exists!")

    def _read(self) -> Generator:
        """Opens a file and yields one line at a time.

        Arguments:
                ...
        Returns:
                Yields (stripped) lines.
        """
        with open(self.ipfile, "r") as ipf:
            for line in ipf.readlines():
                yield line.strip()

    def _grab_ips(self, line: str) -> List[str]:
        """Runs a re.findall on a string.

        Arguments:
                line: str

        Returns:
                list -> [] or ["127.0.0.1",...]
        """
        return re.findall(self.IP_REGEX, line)

    @functools.lru_cache()
    def _parse(self) -> tuple:
        """Does the actual text/ip parsing.
        Reads each line that IPGrabber._read() yields, grabs the IPs and
        converts them to IPv4 object in order to validate them.
        Finally builds a nice dict with the data.

        Arguments:
                ...
        Returns:
                dict -> {ip: IP object, ...}
        """
        ips = {}
        for line in self._read():
            for ip_ in self._grab_ips(line):
                ip = str_to_ipv4(ip_)
                if ip_ in list(ips.keys()):
                    continue
                ips.update(
                    {
                        ip_: IPobject(
                            **{"ip": ip_, "object": ip, "is_valid": ip.is_global}
                        )
                    }
                )

        return tuple(ipobject for ip_, ipobject in ips.items())

    def get_result(self) -> tuple:
        """Returns IPGrabber._parse()"""
        return self._parse()

    def get_result_serialized(self) -> str:
        """A (JSON) serialized version of IPGrabber.get_result"""
        return json.dumps([row.asdict() for row in self.get_result()])
