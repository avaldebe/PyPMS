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
    bridge      MQTT to InfluxDB bridge
"""

from typing import Optional, List
from docopt import docopt
from pms import serial, mqtt, influxdb, bridge, logger


def cli(argv: Optional[List[str]] = None) -> None:
    args = docopt(__doc__, argv, options_first=True)
    try:
        cli = dict(
            serial=serial.cli, mqtt=mqtt.cli, influxdb=influxdb.cli, bridge=bridge.cli
        )[args["<command>"]]
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
