import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
requirements_txt = (HERE / "requirements.txt").read_text().split("\n")

setup(
    name="grait",
    version="0.0.1",
    description="GeoIP queries, RDAP lookups and IP grabbing Tools.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lvm/python_challenge",
    author="Mauro Lizaur",
    author_email="mauro@sdf.org",
    license="BSD 3-Clause License",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["grait"],
    include_package_data=True,
    install_requires=requirements_txt,
    extras_require={"dev": ["flake8", "pylint", "ipython"]},
    entry_points={},
    scripts=["bin/geoip-query", "bin/ipgrabber", "bin/rdap-lookup", "bin/get-geoipcountrywhois"],
)
