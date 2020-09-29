from csv import DictReader, DictWriter
from enum import Enum
from datetime import datetime
from pathlib import Path
from textwrap import wrap

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


def raw(
    ctx: Context,
    capture: bool = Option(False, "--capture", help="save messages to file"),
    decode: Optional[Path] = Option(None, "--decode", help="process messages from file"),
    hexdump: bool = Option(False, "--hexdump", help="print in hexdump format"),
):
    """Capture raw sensor messages"""

    if capture:
        sensor = ctx.obj["reader"].sensor
        path = Path(f"{datetime.now():%F}_pypms.csv")
        echo(f"capture {sensor.name} messages to {path}")
        with ctx.obj["reader"] as reader, path.open("a") as csv:
            writer = DictWriter(csv, fieldnames="time sensor hex".split())
            # add header to new files
            if path.stat().st_size == 0:
                writer.writeheader()
            for raw in reader(raw=True):
                writer.writerow(
                    dict(
                        time=int(datetime.now().timestamp()),
                        sensor=reader.sensor.name,
                        hex=raw.hex(),
                    )
                )
    elif decode:
        sensor = ctx.obj["reader"].sensor
        echo(f"decode {sensor.name} messages from {decode}")
        with decode.open() as csv:
            reader = DictReader(csv)
            for row in reader:
                if row["sensor"] != sensor.name:
                    continue
                echo(sensor.decode(bytes.fromhex(row["hex"]), time=int(row["time"])))

    elif hexdump:
        with ctx.obj["reader"] as reader:
            for n, raw in enumerate(reader(raw=True)):
                msg = " ".join(wrap(raw.hex(), 2))
                prt = "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in raw)
                echo(f"{n*len(raw):08x}: {msg}  {prt}")
    else:
        with ctx.obj["reader"] as reader:
            for raw in reader(raw=True):
                echo(raw.hex())
