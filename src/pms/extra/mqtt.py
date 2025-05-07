from __future__ import annotations

from time import time as seconds_since_epoch
from typing import Callable, NamedTuple, Protocol

from loguru import logger
from paho.mqtt.client import Client


class Publisher(Protocol):
    def __call__(self, data: dict[str, int | float | str]) -> None: ...


def publisher(
    *, topic: str, host: str, port: int, username: str | None, password: str | None
) -> Publisher:
    """returns function to publish to `topic` at `host`"""
    c = Client(client_id=topic)
    c.enable_logger()
    if username:  # pragma: no cover
        c.username_pw_set(username, password)

    c.on_connect = lambda client, userdata, flags, rc: client.publish(
        f"{topic}/$online", "true", 1, True
    )
    c.will_set(f"{topic}/$online", "false", 1, True)
    c.connect(host, port)
    c.loop_start()

    def pub(data: dict[str, int | float | str]) -> None:
        for k, v in data.items():
            c.publish(f"{topic}/{k}", v, 1, True)

    return pub


class Data(NamedTuple):
    time: int
    location: str
    measurement: str
    value: float

    def __str__(self):
        return ",".join(map(str, self))

    @classmethod
    def decode(cls, topic: str, payload: str, *, time: int | None = None) -> Data:
        """Decode MQTT message

        For example
        >>> decode("homie/test/pm10/concentration", "27")
        Data(seconds_since_epoch(), "test", "pm10", 27)
        """
        if not time:
            time = int(seconds_since_epoch())

        fields = topic.split("/")
        if len(fields) != 4:
            raise UserWarning(f"topic total length: {len(fields)}")
        if any([f.startswith("$") for f in fields]):
            raise UserWarning(f"system topic: {topic}")
        location, measurement = fields[1:3]

        try:
            value = float(payload)
        except ValueError as e:
            raise UserWarning(f"non numeric payload: {payload}") from e
        else:
            return cls(time, location, measurement, value)


def subscribe(
    topic: str,
    host: str,
    port: int,
    username: str | None,
    password: str | None,
    *,
    on_sensordata: Callable[[Data], None],
) -> None:
    """subsribe to `topic` at `host` and call `on_sensordata` for every decoded message"""

    def on_message(client: Client, userdata, msg):
        try:
            data = Data.decode(msg.topic, msg.payload)
        except UserWarning as e:
            logger.debug(e)
        else:
            on_sensordata(data)

    c = Client(client_id=topic)
    c.enable_logger()
    if username:  # pragma: no cover
        c.username_pw_set(username, password)

    c.on_connect = lambda client, userdata, flags, rc: client.subscribe(topic)
    c.on_message = on_message
    c.connect(host, port)
    c.loop_forever()
