#!/usr/bin/env python3

import random
import datetime
from typing import Generator


DATE_FORMAT = "%Y-%m-%d"


def from_str_to_dt(dt_str: str) -> datetime.datetime:
    """Converts a date string (yyyy-mm-dd) to datetime"""
    return datetime.datetime.strptime(dt_str, DATE_FORMAT)


def from_dt_to_str(dt_dt: datetime.datetime) -> str:
    """Converts a date string (yyyy-mm-dd) to datetime"""
    return dt_dt.strftime(DATE_FORMAT)


def gen_random_data(days: int = 7) -> Generator:
    """Generates random data for N days with the followin format:

    YYYY-MM-DD,SENDER,RECIPIENT,AMOUNT
    """

    def exclude_from(group: list, thing: str) -> list:
        """Filter a `thing` from a `group`"""
        return [_ for _ in group if _ != thing]

    people = ["john", "mary", "bob", "alice"]
    places = ["insurance", "supermarket", "hospital", "shoes"]
    # just for simplicity, will always start today:
    today = datetime.datetime.now()
    for day in range(days):
        dt = from_dt_to_str(today + datetime.timedelta(days=day))
        sender = random.choice(people)
        recipient = random.choice(places + exclude_from(people, sender))
        amount = random.uniform(0.5, 500.0)
        yield f"{dt},{sender},{recipient},{amount:.2f}"
