from enum import Enum
from pathlib import Path
from typing import Optional
from typer import Context, Option
from .. import logger


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
            for obs in reader():
                print(f"{obs:{format}}")
        else:
            for obs in reader():
                print(str(obs))


def csv(
    ctx: Context,
    filename: str = Option("pms.csv", "--filename", "-F", help="csv formatted file"),
    overwrite: bool = Option(False, "--overwrite", help="overwrite file, if already exists"),
):
    """Read sensor and print measurements"""
    path = Path(filename)
    mode = "w" if overwrite else "a"
    logger.debug(f"open {filename} on '{mode}' mode")
    with ctx.obj["reader"] as reader, path.open(mode) as f:
        # add header to new files
        if path.stat().st_size == 0:
            obs = next(reader())
            print(f"{obs:header}", file=f)
        for obs in reader():
            print(f"{obs:csv}", file=f)
