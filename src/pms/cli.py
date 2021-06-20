import sys
from enum import Enum
from typing import Optional

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from typer import Context, Exit, Option, Typer, echo

from pms import logger
from pms.sensor import SensorReader
from pms.sensor.cli import csv, serial
from pms.service.cli import bridge, influxdb, mqtt

main = Typer(help="Data acquisition and logging tool for PM sensors with UART interface")
main.command()(serial)
main.command()(csv)
main.command()(influxdb)
main.command()(mqtt)
main.command()(bridge)


class Supported(str, Enum):
    PMSx003 = "PMSx003"
    PMS3003 = "PMS3003"
    PMS5003S = "PMS5003S"
    PMS5003ST = "PMS5003ST"
    PMS5003T = "PMS5003T"
    SDS01x = "SDS01x"
    SDS198 = "SDS198"
    HPMA115S0 = "HPMA115S0"
    HPMA115C0 = "HPMA115C0"
    SPS30 = "SPS30"
    MCU680 = "MCU680"
    default = PMSx003


def version_callback(value: bool):  # pragma: no cover
    package = "PyPMS"
    if value:
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
    version: Optional[bool] = Option(None, "--version", callback=version_callback),
):
    """Read serial sensor"""
    if debug:  # pragma: no cover
        logger.setLevel("DEBUG")
    ctx.obj = {"reader": SensorReader(model, port, seconds, samples)}


@main.command()
def info(ctx: Context):
    """Information about the sensor observations"""
    sensor = ctx.obj["reader"].sensor
    echo(sensor.Data.__doc__)
