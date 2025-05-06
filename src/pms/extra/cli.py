import json
import sys
from collections.abc import Iterator
from dataclasses import fields
from typing import Annotated, Optional, Union

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


import typer
from loguru import logger

from pms.core import exit_on_fail
from pms.sensors.base import ObsData

DB_HOST: TypeAlias = Annotated[str, typer.Option("--db-host", help="database server")]
DB_PORT: TypeAlias = Annotated[int, typer.Option("--db-port", help="server port")]
DB_USER: TypeAlias = Annotated[
    str, typer.Option("--db-user", envvar="DB_USER", help="server username")
]
DB_PASS: TypeAlias = Annotated[
    str, typer.Option("--db-pass", envvar="DB_PASS", help="server password")
]
DB_NAME: TypeAlias = Annotated[str, typer.Option("--db-name", help="database name")]


def influxdb(
    ctx: typer.Context,
    host: DB_HOST = "influxdb",
    port: DB_PORT = 8086,
    user: DB_USER = "root",
    word: DB_PASS = "root",
    name: DB_NAME = "homie",
    jtag: Annotated[str, typer.Option("--tags", help="measurement tags")] = json.dumps(
        {"location": "test"}
    ),
):
    """Read sensor and push PM measurements to an InfluxDB server"""
    try:
        from .influxdb import publisher
    except ModuleNotFoundError as e:  # pragma: no cover
        logger.debug(e)
        typer.echo(missing_extras(ctx.command_path, "influxdb"))
        raise typer.Abort() from e

    pub = publisher(host=host, port=port, username=user, password=word, db_name=name)
    tags = json.loads(jtag.replace("'", '"'))

    with exit_on_fail(ctx.obj["reader"]) as reader:
        for obs in reader():
            data = {field.name: getattr(obs, field.name) for field in fields(obs) if field.metadata}
            pub(time=obs.time, tags=tags, data=data)


MQTT_TOPIC: TypeAlias = Annotated[str, typer.Option("--mqtt-topic", help="mqtt root/topic")]
MQTT_HOST: TypeAlias = Annotated[str, typer.Option("--mqtt-host", help="mqtt server")]
MQTT_PORT: TypeAlias = Annotated[int, typer.Option("--mqtt-port", help="server port")]
MQTT_USER: TypeAlias = Annotated[
    Optional[str],
    typer.Option("--mqtt-user", envvar="MQTT_USER", help="server username", show_default=False),
]
MQTT_PASS: TypeAlias = Annotated[
    Optional[str],
    typer.Option("--mqtt-pass", envvar="MQTT_PASS", help="server password", show_default=False),
]


def mqtt(
    ctx: typer.Context,
    topic: Annotated[str, typer.Option("--topic", "-t", help="mqtt root/topic")] = "homie/test",
    host: MQTT_HOST = "test.mosquitto.org",
    port: MQTT_PORT = 1883,
    user: MQTT_USER = None,
    word: MQTT_PASS = None,
):
    """Read sensor and push PM measurements to a MQTT server"""
    try:
        from .mqtt import publisher
    except ModuleNotFoundError as e:  # pragma: no cover
        logger.debug(e)
        typer.echo(missing_extras(ctx.command_path, "mqtt"))
        raise typer.Abort() from e

    publish = publisher(topic=topic, host=host, port=port, username=user, password=word)

    with exit_on_fail(ctx.obj["reader"]) as reader:
        publish(dict(mqtt_messages(next(reader()), sensor_name=ctx.obj["reader"].sensor.name)))
        for obs in reader():
            publish(dict(mqtt_messages(obs)))


def mqtt_messages(
    obs: ObsData, *, sensor_name: Optional[str] = None
) -> Iterator[tuple[str, Union[str, int, float]]]:
    for field in fields(obs):
        if not field.metadata:
            continue
        if sensor_name is not None:
            yield f"{field.name}/$type", field.metadata["long_name"]
            yield f"{field.name}/$properties", f"sensor,unit,{field.metadata['topic']}"
            yield f"{field.name}/sensor", sensor_name
            yield f"{field.name}/unit", field.metadata["units"]
            yield f"{field.name}/{field.metadata['topic']}", getattr(obs, field.name)
        yield f"{field.name}/{field.metadata['topic']}", getattr(obs, field.name)


def bridge(
    ctx: typer.Context,
    mqtt_topic: MQTT_TOPIC = "homie/+/+/+",
    mqtt_host: MQTT_HOST = "test.mosquitto.org",
    mqtt_port: MQTT_PORT = 1883,
    mqtt_user: MQTT_USER = None,
    mqtt_pass: MQTT_PASS = None,
    db_host: DB_HOST = "influxdb",
    db_port: DB_PORT = 8086,
    db_user: DB_USER = "root",
    db_pass: DB_PASS = "root",
    db_name: DB_NAME = "homie",
):
    """Bridge between MQTT and InfluxDB servers"""

    try:
        from .influxdb import publisher
        from .mqtt import Data, subscribe
    except ModuleNotFoundError as e:  # pragma: no cover
        logger.debug(e)
        typer.echo(missing_extras(ctx.command_path, "influxdb", "mqtt"))
        raise typer.Abort() from e

    pub = publisher(host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name)

    def on_sensordata(data: Data) -> None:
        pub(time=data.time, tags={"location": data.location}, data={data.measurement: data.value})

    subscribe(
        topic=mqtt_topic,
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_pass,
        on_sensordata=on_sensordata,
    )


def missing_extras(sub_cmd: str, *extras: str, package: str = "pypms") -> str:  # pragma: no cover
    from functools import partial
    from textwrap import dedent

    green = partial(typer.style, fg=typer.colors.GREEN)
    red = partial(typer.style, fg=typer.colors.RED)
    package = green(package, bold=True)
    extra = ",".join(red(extra, bold=True) for extra in extras)
    msg = f"""
        {green(sub_cmd, bold=True)} require dependencies which are not installed.

        You can install the required dependencies with
            {green("python3 -m pip install --upgrade")} {package}[{extra}]

        Or, if you installed {package} with {green("pipx")}
            {green("pipx install --force")} {package}[{extra}]

        Or, if you installed {package} with {green("uv tool")}
            {green("uv tool install")} {package}[{extra}]
    """
    return dedent(msg)
