#!/user/bin/env python3
from setuptools import setup, find_packages

setup(
    name="PyPMS",
    packages=find_packages(),
    install_requires=[
        "pyserial>=3.4",
        "paho-mqtt>=1.4.0",
        "docopt>=0.6.0",
        "influxdb>=5.2.0",
        "mypy-extensions>=0.4.0",
        "invoke>=1.3.0",
    ],
    entry_points={"console_scripts": ["pms = pms.main:cli.run"]},
)

