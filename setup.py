#!/user/bin/env python3
from setuptools import setup, find_packages
from pms import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="PyPMS",
    version=__version__,
    author="Alvaro Valdebenito",
    author_email="avaldebe@gmail.com",
    description="Python application for PM sensors with serial interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avaldebe/PyPMS",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyserial>=3.4",
        "paho-mqtt>=1.4.0",
        "influxdb>=5.2.0",
        "mypy-extensions>=0.4.0",
        "invoke>=1.3.0",
    ],
    entry_points={"console_scripts": ["pms = pms:program.run"]},
)
