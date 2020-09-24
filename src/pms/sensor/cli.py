from enum import Enum
from pathlib import Path

from typing import Optional
from typer import Context, Option, echo

from pms import logger


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


def serial(
    ctx: Context,
    format: Optional[Format] = Option(None, "--format", "-f", help="formatted output"),
):
    """Read sensor and print measurements"""
    with ctx.obj["reader"] as reader:
        if format:
            if format == "csv":
                obs = next(reader())
                echo(f"{obs:header}")
            for obs in reader():
                echo(f"{obs:{format}}")
        else:
            for obs in reader():
                echo(str(obs))


def csv(
    ctx: Context,
    path: Path = Option(Path("pms.csv"), "--filename", "-F", help="csv formatted file"),
    overwrite: bool = Option(False, "--overwrite", help="overwrite file, if already exists"),
):
    """Read sensor and print measurements"""
    mode = "w" if overwrite else "a"
    logger.debug(f"open {path} on '{mode}' mode")
    with ctx.obj["reader"] as reader, path.open(mode) as f:
        # add header to new files
        if path.stat().st_size == 0:
            obs = next(reader())
            f.write(f"{obs:header}\n")
        for obs in reader():
            f.write(f"{obs:csv}\n")
