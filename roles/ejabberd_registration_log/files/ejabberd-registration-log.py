#!/usr/bin/env python3
"""Consume ejabberd logs and print newly registered users.

The output is printed as CSV records, so it's human and
machine-readable, with the IP-address of the registered user being
resolved to an ASN, its operator and its country of origin.

For testing, remove the match for the ejabberd service and add journal
entries like this:

    echo "The account foo was registered from IP address 1.2.3.4" | systemd-cat

"""

import csv
import json
import re
import selectors
import sys
from functools import lru_cache
from ipaddress import IPv4Address, IPv6Address, ip_address, ip_network
from json import JSONDecodeError
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

import systemd.journal
from systemd.journal import Reader


RIPESTAT_DATA_API_URL = "https://stat.ripe.net/data"


@lru_cache
def get_prefix_info(prefix: IPv4Address | IPv6Address) -> dict[str, Any]:
    """Get IP prefix information from the RIPEStat Data API."""
    response = urlopen(
        f"{RIPESTAT_DATA_API_URL}/prefix-overview/data.json?resource={prefix}"
    )
    if response.getcode() != 200:
        raise URLError("Status code isn't 200")
    return json.loads(response.read())


@lru_cache
def get_country(prefix: str) -> str:
    """Get the country of an IP prefix from the RIPEStat Data API."""
    try:
        response = urlopen(
            f"{RIPESTAT_DATA_API_URL}/rir-geo/data.json?resource={prefix}"
        )
        if response.getcode() != 200:
            return ""
        return json.loads(response.read())["data"]["located_resources"][0]["location"]
    except (AttributeError, JSONDecodeError, URLError):
        return ""


def get_asn(ipaddr: str) -> dict[str, Any] | None:
    """Check if the ASN of an IP-address should be resolved.

    Return ASN information if the IP-address belongs to a publicly
    routed IP prefix, None otherwise.
    """

    try:
        # Check only the possibly longest prefix (longer
        # prefixes are usually not routed/visible via BGP) for
        # better cacheability and to avoid sending users
        # IP addresses.
        prefixlen = 24 if ip_address(ipaddr).version == 4 else 48
        prefix_to_check = ip_network(
            f"{ipaddr}/{prefixlen}", strict=False
        ).network_address
    except ValueError:
        return None

    if (
        prefix_to_check.is_multicast
        or prefix_to_check.is_private
        or prefix_to_check.is_unspecified
        or prefix_to_check.is_reserved
        or prefix_to_check.is_loopback
        or prefix_to_check.is_link_local
    ):
        return None

    try:
        prefix_info = get_prefix_info(prefix_to_check)
    except (AttributeError, JSONDecodeError, URLError):
        return None

    if not prefix_info["data"]["announced"]:
        return None

    return prefix_info


def main():
    reader = Reader()
    reader.add_match("_SYSTEMD_UNIT=ejabberd.service")
    reader.seek_tail()
    reader.get_previous()

    selector = selectors.DefaultSelector()
    selector.register(reader, selectors.EVENT_READ)

    registration_regex = re.compile(
        r"The account (?P<username>\S+) was registered from IP address (?P<ip>[0-9a-f.:]+)$"
    )

    writer = csv.writer(sys.stdout)

    while selector.select():
        state = reader.process()
        if state != systemd.journal.APPEND:
            continue

        for event in reader:
            event_date = event["__REALTIME_TIMESTAMP"]
            result = registration_regex.search(event["MESSAGE"])
            if not result:
                continue

            username = result["username"]
            ipaddr = result["ip"]

            prefix_info = get_asn(ipaddr)

            if not prefix_info:
                writer.writerow([event_date.isoformat(), username, ipaddr, "", "", ""])
                sys.stdout.flush()
                continue

            writer.writerow(
                [
                    event_date.isoformat(),
                    username,
                    ipaddr,
                    str(prefix_info["data"]["asns"][0]["asn"]),
                    prefix_info["data"]["asns"][0]["holder"],
                    get_country(prefix_info["data"]["resource"]),
                ]
            )
            sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
