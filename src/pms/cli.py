import sys
from typing import Optional

if sys.version_info >= (3, 7):  # pragma: no cover
    from enum import Enum
else:  # pragma: no cover
    from aenum import Enum

if sys.version_info >= (3, 8):  # pragma: no cover
    from importlib import metadata
else:  # pragma: no cover
    import importlib_metadata as metadata

from typer import Context, Exit, Option, Typer, echo

from pms import logger
from pms.sensor import Sensor, SensorReader
from pms.sensor.cli import csv, serial
from pms.service.cli import bridge, influxdb, mqtt

main = Typer(help="Data acquisition and logging tool for PM sensors with UART interface")
main.command()(serial)
main.command()(csv)
main.command()(influxdb)
main.command()(mqtt)
main.command()(bridge)


class Supported(str, Enum):
    _ignore_ = "s Supported"

    Supported = vars()
    for s in Sensor:
        Supported[s.name] = s.name

    default = list(Sensor)[0].name


def version_callback(value: bool):  # pragma: no cover
    if not value:
        return

    package = "PyPMS"
    echo(f"{package} version {metadata.version(package)}")
    raise Exit()


@main.callback()
def callback(
    ctx: Context,
    model: Supported = Option(Supported.default, "--sensor-model", "-m", help="sensor model"),
    port: str = Option("/dev/ttyUSB0", "--serial-port", "-s", help="serial port"),
    seconds: int = Option(60, "--interval", "-i", help="seconds to wait between updates"),
    samples: Optional[int] = Option(None, "--samples", "-n", help="stop after N samples"),
    debug: bool = Option(False, "--debug", help="print DEBUG/logging messages"),
    version: Optional[bool] = Option(None, "--version", "-V", callback=version_callback),
):
    """Read serial sensor"""
    if debug:  # pragma: no cover
        logger.setLevel("DEBUG")
    ctx.obj = {"reader": SensorReader(model, port, seconds, samples)}


@main.command()
def info(ctx: Context):  # pragma: no cover
    """Information about the sensor observations"""
    sensor = ctx.obj["reader"].sensor
    echo(sensor.Data.__doc__)
