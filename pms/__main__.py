"""
Read a PMS5003/PMS7003/PMSA003 sensor

Usage:
    pms <command> [<args>...]
    pms <command> --help
    pms --help

Commands:
    serial      print PM measurements
    mqtt        push PM measurements to a MQTT server
    influxdb    push PM measurements to an InfluxDB server
"""

from typing import Optional, List
from docopt import docopt
from pms.serial import cli as serial
from pms.mqtt import cli as mqtt
from pms.influxdb import cli as influxdb
from pms import logger


def cli(argv: Optional[List[str]] = None) -> None:
    args = docopt(__doc__, argv, options_first=True)
    try:
        cli = dict(serial=serial, mqtt=mqtt, influxdb=influxdb)[args["<command>"]]
    except KeyError:
        exit(__doc__)

    try:
        cli([args["<command>"]] + args["<args>"])
    except KeyboardInterrupt:
        print()
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    cli()
