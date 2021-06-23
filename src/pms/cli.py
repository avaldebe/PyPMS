import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 7):  # pragma: no cover
    from enum import Enum
else:  # pragma: no cover
    from aenum import Enum

if sys.version_info >= (3, 10):  # pragma: no cover
    from importlib import metadata
else:  # pragma: no cover
    import importlib_metadata as metadata

from typer import Argument, Context, Exit, Option, Typer, echo

from pms import logger
from pms.sensor import MessageReader, Sensor, SensorReader

main = Typer(help="Data acquisition and logging tool for PM sensors with UART interface")
for ep in metadata.entry_points(group="pypms.extras"):
    main.command(name=ep.name)(ep.load())


class Supported(str, Enum):
    _ignore_ = "s Supported"

    Supported = vars()
    for s in Sensor:  # type: ignore
        Supported[s.name] = s.name

    default = "PMSx003"


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
    bme = "bme"
    bsec = "bsec"
    hex = "hexdump"


@main.command()
def serial(
    ctx: Context,
    format: Optional[Format] = Option(None, "--format", "-f", help="formatted output"),
    decode: Optional[Path] = Option(None, help="decode captured messages"),
):
    """Read sensor and print measurements"""
    reader = ctx.obj["reader"]
    if decode:
        reader = MessageReader(decode, reader.sensor, reader.samples)
    with reader:
        if format == "hexdump":
            for n, raw in enumerate(reader(raw=True)):
                echo(raw.hexdump(n))
        elif format:
            if format == "csv":
                obs = next(reader())
                echo(f"{obs:header}")
            for obs in reader():
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
    """Read sensor and print measurements"""
    if path.is_dir():  # pragma: no cover
        path /= f"{datetime.now():%F}_pypms.csv"
    mode = "w" if overwrite else "a"
    logger.debug(f"open {path} on '{mode}' mode")
    with ctx.obj["reader"] as reader, path.open(mode) as csv:
        sensor_name = reader.sensor.name
        if not capture:
            logger.debug(f"capture {sensor_name} observations to {path}")
            # add header to new files
            if path.stat().st_size == 0:
                obs = next(reader())
                csv.write(f"{obs:header}\n")
            for obs in reader():
                csv.write(f"{obs:csv}\n")
        else:
            logger.debug(f"capture {sensor_name} messages to {path}")
            # add header to new files
            if path.stat().st_size == 0:
                csv.write("time,sensor,hex\n")
            for raw in reader(raw=True):
                csv.write(f"{raw.time},{sensor_name},{raw.hex}\n")
