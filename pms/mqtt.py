from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Callable, NamedTuple
import paho.mqtt.client as mqtt
from .logging import logger


def client_pub(
    *, topic: str, host: str, port: int, username: str, password: str
) -> Callable[[Dict[str, Union[int, str]]], None]:
    c = mqtt.Client(topic)
    c.enable_logger(logger)
    if username:
        c.username_pw_set(username, password)

    c.on_connect = lambda client, userdata, flags, rc: client.publish(
        f"{topic}/$online", "true", 1, True
    )
    c.will_set(f"{topic}/$online", "false", 1, True)
    c.connect(host, port, 60)
    c.loop_start()

    def pub(data: Dict[str, Union[int, str]]) -> None:
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
    def decode(cls, topic: str, payload: str, *, time: Optional[int] = None) -> "Data":
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
    def on_message(client, userdata, msg):
        try:
            data = Data.decode(msg.topic, msg.payload)
        except UserWarning as e:
            logger.debug(e)
        else:
            on_sensordata(data)

    c = mqtt.Client(topic)
    c.enable_logger(logger)
    if username:
        c.username_pw_set(username, password)

    c.on_connect = lambda client, userdata, flags, rc: client.subscribe(topic)
    c.on_message = on_message
    c.connect(host, port, 60)
    c.loop_forever()
