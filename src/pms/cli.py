import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional, Union

import typer
from loguru import logger

from pms import __version__
from pms.core import MessageReader, Sensor, SensorReader, Supported, exit_on_fail

main = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)


def version_callback(value: bool):
    if not value:
        return

    typer.echo(f"PyPMS v{__version__}")
    raise typer.Exit()


@main.callback()
def callback(
    ctx: typer.Context,
    model: Annotated[
        Supported, typer.Option("--sensor-model", "-m", help="sensor model")
    ] = Supported.default,
    port: Annotated[str, typer.Option("--serial-port", "-s", help="serial port")] = "/dev/ttyUSB0",
    interval: Annotated[
        int, typer.Option("--interval", "-i", min=0, help="seconds to wait between updates")
    ] = 60,
    samples: Annotated[
        Optional[int], typer.Option("--samples", "-n", min=1, help="stop after N samples")
    ] = None,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="print DEBUG/logging messages"),
    ] = False,
    version: Annotated[bool, typer.Option("--version", "-V", callback=version_callback)] = False,
):
    """Data acquisition and logging for Air Quality Sensors with UART interface"""
    logger.enable("pms")
    if not debug:  # pragma: no cover
        logger.configure(
            handlers=[
                {"sink": sys.stderr, "format": "<level>{message}</level>", "level": "INFO"},
            ],
        )

    logger.debug(f"PyPMS v{__version__}")
    logger.debug(f"{ctx.command_path} -m {model} ... {ctx.invoked_subcommand}")
    obj = ctx.ensure_object(dict)
    if ctx.invoked_subcommand in {"info", "serial"}:
        obj.update(sensor=Sensor[model], port=port, interval=interval, samples=samples)
    else:
        obj.update(reader=SensorReader(model, port, interval, samples))


@main.command()
def info(ctx: typer.Context):
    """Information about the sensor observations"""
    typer.echo(ctx.obj["sensor"].Data.__doc__)


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

    def __str__(self) -> str:
        return self.value


@main.command()
def serial(
    ctx: typer.Context,
    format: Annotated[
        Optional[Format], typer.Option("--format", "-f", help="formatted output")
    ] = None,
    decode: Annotated[Optional[Path], typer.Option(help="decode captured messages")] = None,
):
    """Read sensor and print formatted measurements"""
    reader: Union[SensorReader, MessageReader]
    if decode:
        reader = MessageReader(decode, ctx.obj["sensor"], ctx.obj["samples"])
    else:
        reader = SensorReader(**ctx.obj)

    with exit_on_fail(reader):
        if format == "hexdump":
            for n, raw in enumerate(reader(raw=True)):
                typer.echo(raw.hexdump(n))
        elif format:
            print_header = format == "csv"
            for obs in reader():
                if print_header:
                    typer.echo(f"{obs:header}")
                    print_header = False
                typer.echo(f"{obs:{format}}")
        else:
            for obs in reader():
                typer.echo(str(obs))


@main.command()
def csv(
    ctx: typer.Context,
    capture: Annotated[
        bool, typer.Option("--capture", help="write raw messages instead of observations")
    ] = False,
    overwrite: Annotated[
        bool, typer.Option("--overwrite", help="overwrite file, if already exists")
    ] = False,
    path: Annotated[Path, typer.Argument(help="csv formatted file", show_default=False)] = Path(),
):
    """Read sensor and save measurements to a CSV file"""
    if path.is_dir():  # pragma: no cover
        path /= f"{datetime.now():%F}_pypms.csv"
    mode = "w" if overwrite else "a"
    logger.debug(f"open {path} on '{mode}' mode")

    with exit_on_fail(ctx.obj["reader"]) as reader, path.open(mode) as csv:
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
