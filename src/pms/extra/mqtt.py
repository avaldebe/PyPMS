from __future__ import annotations

from dataclasses import fields
from datetime import datetime
from typing import Annotated, Callable, NamedTuple

import typer
from loguru import logger
from paho.mqtt.client import Client

from pms.core import exit_on_fail
from pms.sensors.base import ObsData


def client_pub(
    *, topic: str, host: str, port: int, username: str, password: str
) -> Callable[[dict[str, int | str]], None]:
    c = Client(client_id=topic)
    c.enable_logger(logger)  # type:ignore[arg-type]
    if username:
        c.username_pw_set(username, password)

    c.on_connect = lambda client, userdata, flags, rc: client.publish(
        f"{topic}/$online", "true", 1, True
    )
    c.will_set(f"{topic}/$online", "false", 1, True)
    c.connect(host, port)
    c.loop_start()

    def pub(data: dict[str, int | str]) -> None:
        for k, v in data.items():
            c.publish(f"{topic}/{k}", v, 1, True)

    return pub


class Data(NamedTuple):
    time: int
    location: str
    measurement: str
    value: float

    @staticmethod
    def now() -> int:
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())

    @classmethod
    def decode(cls, topic: str, payload: str, *, time: int | None = None) -> Data:
        """Decode a MQTT message

        For example
        >>> decode("homie/test/pm10/concentration", "27")
        >>> Data(now(), "test", "pm10", 27)
        """
        if not time:
            time = cls.now()

        fields = topic.split("/")
        if len(fields) != 4:
            raise UserWarning(f"topic total length: {len(fields)}")
        if any([f.startswith("$") for f in fields]):
            raise UserWarning(f"system topic: {topic}")
        location, measurement = fields[1:3]

        try:
            value = float(payload)
        except ValueError:
            raise UserWarning(f"non numeric payload: {payload}")
        else:
            return cls(time, location, measurement, value)


def client_sub(
    topic: str,
    host: str,
    port: int,
    username: str,
    password: str,
    *,
    on_sensordata: Callable[[Data], None],
) -> None:
    def on_message(client: Client, userdata, msg):
        try:
            data = Data.decode(msg.topic, msg.payload)
        except UserWarning as e:
            logger.debug(e)
        else:
            on_sensordata(data)

    c = Client(client_id=topic)
    c.enable_logger(logger)  # type:ignore[arg-type]
    if username:
        c.username_pw_set(username, password)

    c.on_connect = lambda client, userdata, flags, rc: client.subscribe(topic)
    c.on_message = on_message
    c.connect(host, port)
    c.loop_forever()


def cli(
    ctx: typer.Context,
    topic: Annotated[str, typer.Option("--topic", "-t", help="mqtt root/topic")] = "homie/test",
    host: Annotated[str, typer.Option("--mqtt-host", help="mqtt server")] = "mqtt.eclipse.org",
    port: Annotated[int, typer.Option("--mqtt-port", help="server port")] = 1883,
    user: Annotated[
        str,
        typer.Option("--mqtt-user", envvar="MQTT_USER", help="server username", show_default=False),
    ] = "",
    word: Annotated[
        str,
        typer.Option("--mqtt-pass", envvar="MQTT_PASS", help="server password", show_default=False),
    ] = "",
):
    """Read sensor and push PM measurements to a MQTT server"""
    pub = client_pub(topic=topic, host=host, port=port, username=user, password=word)

    def publish(obs: ObsData, metadata: bool = False):
        data = {}
        for field in fields(obs):
            if not field.metadata:
                continue
            if metadata:
                data[f"{field.name}/$type"] = field.metadata["long_name"]
                data[f"{field.name}/$properties"] = f"sensor,unit,{field.metadata['topic']}"
                data[f"{field.name}/sensor"] = ctx.obj["reader"].sensor.name
                data[f"{field.name}/unit"] = field.metadata["units"]
            data[f"{field.name}/{field.metadata['topic']}"] = getattr(obs, field.name)
        pub(data)

    with exit_on_fail(ctx.obj["reader"]) as reader:
        publish(next(reader()), metadata=True)
        for obs in reader():
            publish(obs)
