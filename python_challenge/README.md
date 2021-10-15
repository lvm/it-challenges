# grait: GeoIP queries, RDAP lookups and IP grabbing Tools.

As the name suggests this project contains tools to find out the country of origin of an IP and some extra data. Also to scrape the IPs from a text file.

## Contents


This project provides a Python module, named `grait`, and 4 CLI apps.


### `get-geoipcountrywhois`

A Python CLI app to download `GeoIPCountryWhois.csv` (a requirement of `geoip-query`)
```
usage: get-geoipcountrywhois [-h] filename

positional arguments:
  filename    Where to store the Geo Legacy file.

optional arguments:
  -h, --help  show this help message and exit

```


### `ipgrabber`

A Python CLI app to scrape IPs from a plain text file

```
usage: ipgrabber [-h] [--json] ipfile

positional arguments:
  ipfile      File with IPs

optional arguments:
  -h, --help  show this help message and exit
  --json      Print results as JSON
```

### `geoip-query`

A Python CLI app to GeoIP locate an IP.
```
usage: geoip-query [-h] [--json] geofile ipaddr

positional arguments:
  geofile     Geo Legacy CSV File
  ipaddr      IP Address to Localize. Multi IPs are valid but separated by a comma. Ex: 10.1.2.3,200.55.11.2

optional arguments:
  -h, --help  show this help message and exit
  --json      Print results as JSON
```

### `rdap-lookup`

A Python CLI app to obtain RDAP data from IP.
```
rdap-lookup --help
usage: rdap-lookup [-h] [--json] ipaddr

positional arguments:
  ipaddr      IP Address to Localize. Multi IPs are valid but separated by a comma. Ex: 10.1.2.3,200.55.11.2

optional arguments:
  -h, --help  show this help message and exit
  --json      Print results as JSON
```



## How to...

### Install

There are two ways:

Directly from Github
```
$ pip install -e git://github.com/lvm/python_challenge.git@0.0.1#egg=grait
```

Cloning and manually `setup.py build && install`
```
$ git clone https://github.com/lvm/python_challenge.git
$ cd python_challenge/
$ python3 setup.py build
$ python3 setup.py install --user
```

### Run

> Note: `jq` is a 3rd party app! You can download it [from here](https://stedolan.github.io/jq/).

Once installed, download the `GeoIPCountryWhois.csv` file:

```
$ get-geoipcountrywhois ~/GeoIPCountryWhois.csv
```

Then you can start making geoip queries:

```
$ geoip-query ~/GeoIPCountryWhois.csv 91.68.35.27,194.53.172.52 --json | jq
```

Or RDAP Lookups, if you're into that:

```
$ rdap-lookup/app 124.70.169.32 --json | jq
```

Ran out of IPs? No worries:

```
$ ipgrabber ~/file_with_ips_in_it.txt --json | jq  .[].ip
```

Just valid ips?
```
$ ipgrabber ~/file_with_ips_in_it.txt --json | jq 'map(select(.is_valid == true)) | .[].ip'
```

### Combine

Grab ips from a text file and query their location:

```
$ IP_LIST=`ipgrabber ~/file_with_ips_in_it.txt --json | jq 'map(select(.is_valid == true)) | .[].ip' | sed 's,",,g' | tr '\n' ','`
$ geoip-query ~/GeoIPCountryWhois.csv $IP_LIST --json | jq
```


### Test

Test everything
```
$ python3 -m unittest discover tests/
```

Or individually:
```
$ python3 -m unittest tests/test_grabber.py
$ python3 -m unittest tests/test_geoip.py
$ python3 -m unittest tests/test_rdap.py
```

## License

See [LICENSE](LICENSE)
