"""Data acquisition and logging tool for PM sensors with UART interface"""

import json
from enum import Enum
from pathlib import Path
from typing import Optional
import typer
from . import logger, service, sensor


cli = typer.Typer(help=__doc__)


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
    default = PMSx003


@cli.callback()
def main(
    ctx: typer.Context,
    model: Supported = typer.Option(Supported.default, "--sensor-model", "-m", help="sensor model"),
    port: str = typer.Option("/dev/ttyUSB0", "--serial-port", "-s", help="serial port"),
    seconds: int = typer.Option(60, "--interval", "-i", help="seconds to wait between updates"),
    debug: bool = typer.Option(False, "--debug", help="print DEBUG/logging messages"),
):
    """Read serial sensor"""
    if debug:
        logger.setLevel("DEBUG")
    ctx.obj = {"reader": sensor.SensorReader(model, port, seconds)}


class Format(str, Enum):
    csv = "csv"
    pm = "pm"
    num = "num"
    raw = "raw"
    cf = "cf"
    atm = "atm"
    hcho = "hcho"


@cli.command()
def serial(
    ctx: typer.Context,
    format: Optional[Format] = typer.Option(None, "--format", "-f", help="formatted output"),
):
    """Read sensor and print measurements"""
    with ctx.obj["reader"] as reader:
        if format:
            for obs in reader():
                print(f"{obs:{format}}")
        else:
            for obs in reader():
                print(str(obs))


@cli.command()
def csv(
    ctx: typer.Context,
    filename: str = typer.Option("pms.csv", "--filename", "-F", help="csv formatted file"),
    overwrite: bool = typer.Option(False, "--overwrite", help="overwrite file, if already exists"),
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


@cli.command()
def mqtt(
    ctx: typer.Context,
    topic: str = typer.Option("homie/test", "--topic", "-t", help="mqtt root/topic"),
    host: str = typer.Option("mqtt.eclipse.org", "--mqtt-host", help="mqtt server"),
    port: int = typer.Option(1883, "--mqtt-port", help="server port"),
    user: str = typer.Option("", "--mqtt-user", help="server username", show_default=False),
    word: str = typer.Option("", "--mqtt-pass", help="server password", show_default=False),
):
    """Read sensor and push PM measurements to a MQTT server"""
    pub = service.mqtt.client_pub(topic=topic, host=host, port=port, username=user, password=word)
    for k, v in {"pm01": "PM1", "pm25": "PM2.5", "pm10": "PM10"}.items():
        pub(
            {
                f"{k}/$type": v,
                f"{k}/$properties": "sensor,unit,concentration",
                f"{k}/sensor": ctx.obj["reader"].sensor.name,
                f"{k}/unit": "ug/m3",
            }
        )
    with ctx.obj["reader"] as reader:
        for obs in reader():
            pub({f"{k}/concentration": v for k, v in obs.subset("pm").items()})


@cli.command()
def influxdb(
    ctx: typer.Context,
    host: str = typer.Option("influxdb", "--db-host", help="database server"),
    port: int = typer.Option(8086, "--db-port", help="server port"),
    user: str = typer.Option("root", "--db-user", help="server username"),
    word: str = typer.Option("root", "--db-pass", help="server password"),
    name: str = typer.Option("homie", "--db-name", help="database name"),
    jtag: str = typer.Option("{'location':'test'}", "--tags", help="measurement tags"),
):
    """Read sensor and push PM measurements to an InfluxDB server"""
    pub = service.influxdb.client_pub(
        host=host, port=port, username=user, password=word, db_name=name
    )
    tags = json.loads(jtag)
    with ctx.obj["reader"] as reader:
        for obs in reader():
            pub(time=obs.time, tags=tags, data=obs.subset("pm"))


@cli.command()
def bridge(
    mqtt_topic: str = typer.Option("homie/+/+/+", help="mqtt root/topic"),
    mqtt_host: str = typer.Option("mqtt.eclipse.org", help="mqtt server"),
    mqtt_port: int = typer.Option(1883, help="server port"),
    mqtt_user: str = typer.Option("", help="server username", show_default=False),
    mqtt_pass: str = typer.Option("", help="server password", show_default=False),
    db_host: str = typer.Option("influxdb", help="database server"),
    db_port: int = typer.Option(8086, help="server port"),
    db_user: str = typer.Option("root", help="server username"),
    db_pass: str = typer.Option("root", help="server password"),
    db_name: str = typer.Option("homie", help="database name"),
):
    """Bridge between MQTT and InfluxDB servers"""
    pub = service.influxdb.client_pub(
        host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name
    )

    def on_sensordata(data: service.mqtt.Data) -> None:
        pub(time=data.time, tags={"location": data.location}, data={data.measurement: data.value})

    service.mqtt.client_sub(
        topic=mqtt_topic,
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_pass,
        on_sensordata=on_sensordata,
    )
