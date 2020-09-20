"""Data acquisition and logging tool for PM sensors with UART interface"""

from enum import Enum
from typer import Typer, Context, Option
from . import logger
from .sensor import SensorReader
from .sensor.cli import serial, csv
from .service.cli import influxdb, mqtt, bridge


main = Typer(help=__doc__)
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


@main.callback()
def callback(
    ctx: Context,
    model: Supported = Option(Supported.default, "--sensor-model", "-m", help="sensor model"),
    port: str = Option("/dev/ttyUSB0", "--serial-port", "-s", help="serial port"),
    seconds: int = Option(60, "--interval", "-i", help="seconds to wait between updates"),
    debug: bool = Option(False, "--debug", help="print DEBUG/logging messages"),
):
    """Read serial sensor"""
    if debug:
        logger.setLevel("DEBUG")
    ctx.obj = {"reader": SensorReader(model, port, seconds)}
