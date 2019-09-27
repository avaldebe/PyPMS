from invoke import Program, Collection
from .logging import logger
from .sensor import PMSerial
from . import serial, mqtt, influxdb, bridge

__version__ = "0.0.0"

program = Program(
    version=__version__,
    namespace=Collection(serial.main, mqtt.main, influxdb.main, bridge.main),
    name=__name__,
)
