#!/usr/bin/env python3

import io
import csv
import datetime

from pathlib import Path

from typing import List
from typing import Union
from typing import Literal
from typing import Optional
from typing import Generator

from dataclasses import field
from dataclasses import asdict
from dataclasses import dataclass

from .helpers import from_str_to_dt


@dataclass
class Balance:
    who: str
    spent: float = field(default=0.0)
    received: float = field(default=0.0)
    balance: float = field(default=0.0)

    def as_dict(self) -> Literal[None]:
        return asdict(self)

    def _calc_balance(self) -> Literal[None]:
        self.balance = round(self.received - self.spent, 2)

    def money_out(self, amount: Union[str, float]) -> Literal[None]:
        self.spent += round(float(amount))
        self._calc_balance()

    def money_in(self, amount: Union[str, float]) -> Literal[None]:
        self.received += round(float(amount))
        self._calc_balance()


class Finances:
    COLUMNS = ["date", "sender", "recipient", "amount"]

    def __init__(self, infile: Path) -> Literal[None]:
        self.infile = infile
        self._data = []
        self._load_data()

    def _load_data(self) -> Literal[None]:
        """Reads the Finances file (a headerless csv file)"""
        if isinstance(self.infile, io.StringIO):
            infile = self.infile
        else:
            infile = self.infile.open("r")

        data = []
        # Sort of emulates csv.DictReader
        lines = csv.reader(infile, delimiter=",")
        for line in lines:
            data.append({col: line[i].strip() for i, col in enumerate(self.COLUMNS)})
        self._data = data

    def filter_row(self, row: dict, filters: dict, strict: bool = True) -> bool:
        """Filters a row given a set of filters.

        Strict mode will use `all()`
        -> {"date__lte": "2021-09-29"}, Strict = True
        [PASS]
        {'date': '2021-09-28', 'sender': 'bob',
         'recipient': 'mary', 'amount': '154.74'}

        [PASS]
        {'date': '2021-09-29', 'sender': 'mary',
         'recipient': 'supermarket', 'amount': '130.87'}

        [FAIL]
        {'date': '2021-09-30', 'sender': 'bob',
         'recipient': 'mary', 'amount': '362.01'}

        Non Strict mode will use `any()`
        -> {"sender": "bob", "recipient":"bob"}, Strict = False
        [FAIL]
        {'date': '2021-10-01', 'sender': 'john',
         'recipient': 'alice', 'amount': '473.13'}

        [PASS]
        {'date': '2021-10-02', 'sender': 'bob',
         'recipient': 'supermarket', 'amount': '251.10'}

        [PASS]
        {'date': '2021-10-03', 'sender': 'mary',
         'recipient': 'bob', 'amount': '67.54'}
        """

        def match(
            row: dict, key: str, value: Union[datetime.datetime, str, float]
        ) -> bool:
            """Returns t/f if the key + lookup matches the current row value"""
            lookup = None
            if "__" in key:
                key, lookup = key.split("__")

            # in case we're dealing with dates, we need to convert
            # them to a format that can be easily compared, such as:
            if key == "date" and isinstance(value, str):
                value = from_str_to_dt(value)

            # same thing with the row's (current) value:
            current_value = row.get(key, None)
            if isinstance(value, datetime.datetime):
                current_value = from_str_to_dt(current_value)

            # but before doing any cmp,
            # lets see if curr_value and value type match
            if type(current_value) != type(value):
                return False

            matches = False
            if not lookup:
                matches = current_value == value
            elif lookup == "lte":
                matches = current_value <= value
            elif lookup == "gte":
                matches = current_value >= value

            return matches

        row_matches = [match(row, key, value) for key, value in filters.items()]
        if strict:
            return all(row_matches)

        return any(row_matches)

    def lazy_filter_row(self, row: dict, filters: dict) -> bool:
        return self.filter_row(row, filters, False)

    def get_data(self) -> Generator:
        """Yields the Financial report as a dict"""
        for row in self._data:
            yield row

    def get_data_for(
        self, who: str, until: Optional[Union[str, datetime.datetime]] = None
    ) -> Generator:
        """Yields the Financial Balance for someone/someplace
        Optionally: until some date.
        """

        for row in self.get_data():
            # Ugly code ahead:
            # yield if:
            # * send/rcpt is `who` and if there's also a date and that date is lte `until`.
            # * send/rcpt is `who` and there isn't a date.

            if self.lazy_filter_row(row, {"sender": who, "recipient": who}):
                if until:
                    if self.filter_row(row, {"date__lte": until}):
                        yield row
                else:
                    yield row

    def get_data_until(self, until: Union[str, datetime.datetime]) -> Generator:
        """Yields the Financial Balance until some date."""

        for row in self.get_data():
            if self.filter_row(row, {"date__lte": until}):
                yield row

    def get_balance_for(
        self, who: str, until: Optional[Union[str, datetime.datetime]] = None
    ) -> dict:
        """Returns a Balance for a person/place (optionally: until a date)."""

        balance = Balance(who)
        for row in self.get_data_for(who, until):
            if who == row.get("sender"):
                balance.money_out(row.get("amount"))
            if who == row.get("recipient"):
                balance.money_in(row.get("amount"))

        return balance.as_dict()

    def get_balance_until(
        self, until: Optional[Union[str, datetime.datetime]] = None
    ) -> dict:
        """Returns a Balance from all until a date."""

        def manage_balances(balances: dict, who: str) -> List[Union[dict, Balance]]:
            """From a dict that stores `Balance`s, will look for a particular
            balance that belongs to `who`. If not found, will create it.
            """
            if who and who not in balances.keys():
                balances.update({who: Balance(who)})
            return balances, balances.get(who, None)

        if until:
            data = self.get_data_until(until)
        else:
            data = self.get_data()

        balances, _ = manage_balances({}, "")
        for row in data:
            balances, s_balance = manage_balances(balances, row.get("sender"))
            balances, r_balance = manage_balances(balances, row.get("recipient"))

            s_balance.money_out(row.get("amount"))
            r_balance.money_in(row.get("amount"))

        return {who: balance.as_dict() for who, balance in balances.items()}

    def get_balance(self) -> dict:
        """Provides the Balances from all for all days"""
        return self.get_balance_until()
