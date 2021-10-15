import io
import datetime
from unittest import TestCase

from balance import Balance
from balance import Finances
from balance import from_str_to_dt
from balance import from_dt_to_str
from balance import gen_random_data


TEST_DATA = """2021-09-29,alice,john,469.81
2021-09-30,mary,shoes,142.17
2021-10-01,bob,alice,31.79
2021-10-02,alice,mary,377.23
2021-10-03,alice,hospital,492.37
2021-10-04,bob,alice,309.11
2021-10-05,mary,alice,295.88
2021-10-06,bob,john,142.77
2021-10-07,bob,mary,388.51
2021-10-08,john,supermarket,232.09
"""


class FinancesTestCase(TestCase):
    def setUp(self):
        self.test_data = io.StringIO(TEST_DATA)
        self.finances = Finances(self.test_data)

    def test_balance(self):
        "Balance dataclass"
        b = Balance("test")
        b.money_in(23)
        b.money_out(12)
        b.money_in(5)
        b.money_out(7)
        self.assertEqual(b.balance, 9)

    def test_gen_random_data(self):
        "Generate random testing data"
        data = list(gen_random_data(7))
        self.assertEqual(len(data), 7)

    def test_datetime_str(self):
        "datetime to str and visceversa"
        dt = datetime.datetime.now()
        self.assertIsInstance(from_dt_to_str(dt), str)
        self.assertIsInstance(from_str_to_dt(from_dt_to_str(dt)), datetime.datetime)

        dt_str = "2021-09-28"
        self.assertIsInstance(from_str_to_dt(dt_str), datetime.datetime)
        self.assertIsInstance(from_dt_to_str(from_str_to_dt(dt_str)), str)

    def test_get_data(self):
        "Finances.get_data"
        data = list(self.finances.get_data())
        self.assertEqual(len(data), 10)

    def test_get_data_for(self):
        "Finances.get_data_for"
        bob_data = list(self.finances.get_data_for("bob"))
        self.assertEqual(len(bob_data), 4)

    def test_get_data_for_until(self):
        "Finances.get_data_for"
        alice_data = list(self.finances.get_data_for("alice", "2021-10-05"))
        self.assertEqual(len(alice_data), 6)

    def test_get_data_until(self):
        "Finances.get_data_until"
        until_data = list(self.finances.get_data_until("2021-10-06"))
        self.assertEqual(len(until_data), 8)

    def test_get_balance_for(self):
        "Finances.get_balance_for"
        bob_balance = self.finances.get_balance_for("bob")
        self.assertEqual(bob_balance.get("balance"), -873.0)
        self.assertEqual(bob_balance.get("received"), 0.0)

    def test_get_balance_for_until(self):
        "Finances.get_balance_for"
        alice_balance = self.finances.get_balance_for("alice", "2021-10-05")
        self.assertEqual(alice_balance.get("balance"), -702.0)
        self.assertEqual(alice_balance.get("spent"), 1339.0)

    def test_get_balance_until(self):
        "Finances.get_balance_until"
        until_balance = self.finances.get_balance_until("2021-10-05")
        self.assertEqual(len(until_balance), 6)
        self.assertEqual(until_balance.get("shoes").get("balance"), 142.0)

    def test_get_balance(self):
        "Finances.get_balance"
        balance = self.finances.get_balance()
        self.assertEqual(len(balance), 7)
        self.assertEqual(balance.get("hospital").get("spent"), 0.0)
        self.assertEqual(balance.get("supermarket").get("spent"), 0.0)
        self.assertEqual(balance.get("shoes").get("spent"), 0.0)
