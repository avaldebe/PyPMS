import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 10):  # pragma: no cover
    from importlib import metadata
else:  # pragma: no cover
    import importlib_metadata as metadata

from typer import Argument, Context, Exit, Option, Typer, echo

from pms import logger
from pms.core import MessageReader, SensorReader, Supported

main = Typer(help="Data acquisition and logging for Air Quality Sensors with UART interface")

"""
Extra cli commands from plugins

additional Typer commands are loaded from plugins (entry points) advertized as `"pypms.extras"`
"""
for ep in metadata.entry_points(group="pypms.extras"):
    main.command(name=ep.name)(ep.load())


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


class Format(str, Enum):
    csv = "csv"
    pm = "pm"
    num = "num"
    raw = "raw"
    cf = "cf"
    atm = "atm"
    hcho = "hcho"
    co2 = "co2"
    bme = "bme"
    bsec = "bsec"
    hex = "hexdump"


@main.command()
def serial(
    ctx: Context,
    format: Optional[Format] = Option(None, "--format", "-f", help="formatted output"),
    decode: Optional[Path] = Option(None, help="decode captured messages"),
):
    """Read sensor and print formatted measurements"""
    reader = ctx.obj["reader"]
    if decode:
        reader = MessageReader(decode, reader.sensor, reader.samples)
    with reader:
        if format == "hexdump":
            for n, raw in enumerate(reader(raw=True)):
                echo(raw.hexdump(n))
        elif format:
            print_header = format == "csv"
            for obs in reader():
                if print_header:
                    echo(f"{obs:header}")
                    print_header = False
                echo(f"{obs:{format}}")
        else:  # pragma: no cover
            for obs in reader():
                echo(str(obs))


@main.command()
def csv(
    ctx: Context,
    capture: bool = Option(False, "--capture", help="write raw messages instead of observations"),
    overwrite: bool = Option(False, "--overwrite", help="overwrite file, if already exists"),
    path: Path = Argument(Path(), help="csv formatted file", show_default=False),
):
    """Read sensor and save measurements to a CSV file"""
    if path.is_dir():  # pragma: no cover
        path /= f"{datetime.now():%F}_pypms.csv"
    mode = "w" if overwrite else "a"
    logger.debug(f"open {path} on '{mode}' mode")
    with ctx.obj["reader"] as reader, path.open(mode) as csv:
        sensor_name = reader.sensor.name
        if not capture:
            logger.debug(f"capture {sensor_name} observations to {path}")
            # add header to new files
            print_header = path.stat().st_size == 0
            for obs in reader():
                if print_header:
                    csv.write(f"{obs:header}\n")
                    print_header = False
                csv.write(f"{obs:csv}\n")
        else:
            logger.debug(f"capture {sensor_name} messages to {path}")
            # add header to new files
            if path.stat().st_size == 0:
                csv.write("time,sensor,hex\n")
            for raw in reader(raw=True):
                csv.write(f"{raw.time},{sensor_name},{raw.hex}\n")
