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
    description="Read PM sensors with serial interface, data acquisition and logging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avaldebe/PyPMS",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Terminals :: Serial",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyserial>=3.4",
        "paho-mqtt>=1.4.0",
        "influxdb>=5.2.0",
        "mypy-extensions>=0.4.0",
        "click>=7.0",
    ],
    entry_points={"console_scripts": ["pms = pms.cli:main"]},
)
