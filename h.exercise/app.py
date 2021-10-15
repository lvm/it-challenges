#!/usr/bin/env python3

import argparse
from pathlib import Path
from balance import Finances
from balance import gen_random_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Financial file with reports", nargs="?")
    parser.add_argument(
        "--gen-data",
        help="Generates random test data for [N] days.",
        type=int,
        required=False,
        default=0,
    )
    parser.add_argument(
        "--get-balance", action="store_true", default=False, help="Get the balance."
    )
    parser.add_argument("--balance-for", help="Get a person/place balance.")
    parser.add_argument(
        "--balance-until", help="Get the balance until a date. Use format: YYYY-MM-DD"
    )

    args = parser.parse_args()
    if args.gen_data:
        for data in gen_random_data(args.gen_data):
            print(data)
    elif args.infile and args.get_balance:
        infile = Path(args.infile)
        assert infile.exists(), FileNotFoundError("Missing financial report.")
        f = Finances(infile)
        if args.balance_for:
            if args.balance_until:
                data = f.get_balance_for(args.balance_for, args.balance_until)
            else:
                data = f.get_balance_for(args.balance_for)
        elif args.balance_until:
            data = f.get_balance_until(args.balance_until)
        else:
            data = f.get_balance()
        print(data)
    else:
        parser.print_help()
