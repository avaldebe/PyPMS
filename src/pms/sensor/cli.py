from enum import Enum
from datetime import datetime
from pathlib import Path
from textwrap import wrap

from typing import Optional
from typer import Context, Option, Argument, echo

from pms import logger
from pms.sensor import MesageReader


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


def serial(
    ctx: Context,
    format: Optional[Format] = Option(None, "--format", "-f", help="formatted output"),
    decode: Optional[Path] = Option(None, help="decode captured messages"),
):
    """Read sensor and print measurements"""
    reader = ctx.obj["reader"]
    if decode:
        reader = MesageReader(decode, reader.sensor, reader.samples)
    with reader:
        if format == "hexdump":
            table = bytes.maketrans(
                bytes(range(0x20)) + bytes(range(0x7E, 0x100)), b"." * (0x20 + 0x100 - 0x7E)
            )
            for n, raw in enumerate(reader(raw=True)):
                msg = " ".join(wrap(raw.hex(), 2))  # raw.hex(" ") in python3.8+
                prt = raw.translate(table).decode()
                echo(f"{n*len(raw):08x}: {msg}  {prt}")
        elif format:
            if format == "csv":
                obs = next(reader())
                echo(f"{obs:header}")
            for obs in reader():
                echo(f"{obs:{format}}")
        else:  # pragma: no cover
            for obs in reader():
                echo(str(obs))


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
                time = int(datetime.now().timestamp())
                csv.write(f"{time},{sensor_name},{raw.hex()}\n")
