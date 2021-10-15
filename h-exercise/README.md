# h.is

Hello there, this is a simple exercise. You'll probably won't find anything of interest... unless you do. If that's the case, keep reading.


# How to

Note:
This project uses standard-lib modules available in Python 3.8+ only, yet there are some utilities that were used while writing this:

* black
* flake8
* prospector

But these are code analysis/style tools and go beyond the scope.

That being said:

```
$ python3 app.py --help
usage: app.py [-h] [--gen-data GEN_DATA] [--get-balance] [--balance-for BALANCE_FOR] [--balance-until BALANCE_UNTIL] [infile]

positional arguments:
  infile                Financial file with reports

optional arguments:
  -h, --help            show this help message and exit
  --gen-data GEN_DATA   Generates random test data for [N] days.
  --get-balance         Get the balance.
  --balance-for BALANCE_FOR
                        Get a person/place balance.
  --balance-until BALANCE_UNTIL
                        Get the balance until a date. Use format: YYYY-MM-DD

```


# Testing

```
$ python3 -m unittest tests/test_finances.py
...........
----------------------------------------------------------------------
Ran 11 tests in 0.005s

OK
```
