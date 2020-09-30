from enum import Enum
from typing import Optional

from typer import Typer, Context, Option, echo, Exit

from pms import logger, __doc__, __version__
from pms.sensor import SensorReader
from pms.sensor.cli import serial, csv
from pms.service.cli import influxdb, mqtt, bridge


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


def version_callback(value: bool):  # pragma: no cover
    if value:
        name = __name__.split(".")[0]
        echo(f"{name} version {__version__}")
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
