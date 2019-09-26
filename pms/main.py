from typing import Callable
from invoke import Program, Collection
from pms import __version__, serial, mqtt, influxdb, bridge

ns = Collection(serial.main, mqtt.main, influxdb.main, bridge.main)
cli = Program(namespace=ns, version=__version__)
