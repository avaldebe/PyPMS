from dataclasses import fields
from datetime import datetime
from typing import Callable, Dict, NamedTuple, Union

from typer import Abort, Context, Option, colors, echo, style

try:
    from paho.mqtt import client  # type: ignore
except ModuleNotFoundError:
    client = None  # type: ignore

from pms import logger
from pms.sensors.base import ObsData


def __missing_mqtt():  # pragma: no cover
    name = style(__name__, fg=colors.GREEN, bold=True)
    package = style("pypms", fg=colors.GREEN, bold=True)
    module = style("paho-mqtt", fg=colors.RED, bold=True)
    extra = style("mqtt", fg=colors.RED, bold=True)
    pip = style("python3 -m pip install --upgrade", fg=colors.GREEN)
    pipx = style("pipx inject", fg=colors.GREEN)
    echo(
        f"""
{name} provides additional functionality to {package}.
This functionality requires the {module} module, which is not installed.
You can install this additional dependency with
\t{pip} {package}[{extra}]
Or, if you installed {package} with pipx
\t{pipx} {package} {module}
"""
    )
    raise Abort()


def client_pub(
    *, topic: str, host: str, port: int, username: str, password: str
) -> Callable[[Dict[str, Union[int, str]]], None]:  # pragma: no cover
    if client is None:
        __missing_mqtt()
    c = client.Client(topic)
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
    def now() -> int:  # pragma: no cover
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())

    @classmethod
    def decode(cls, topic: str, payload: str, *, time: int = None) -> "Data":
        """Decode a MQTT message

        For example
        >>> decode("homie/test/pm10/concentration", "27")
        >>> Data(now(), "test", "pm10", 27)
        """
        if not time:  # pragma: no cover
            time = cls.now()

        fields = topic.split("/")
        if len(fields) != 4:
            raise UserWarning(f"topic total length: {len(fields)}")
        if any([f.startswith("$") for f in fields]):
            raise UserWarning(f"system topic: {topic}")
        location, measurement = fields[1:3]

        try:
            value = float(payload)
        except ValueError:  # pragma: no cover
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
) -> None:  # pragma: no cover
    def on_message(client, userdata, msg):
        try:
            data = Data.decode(msg.topic, msg.payload)
        except UserWarning as e:
            logger.debug(e)
        else:
            on_sensordata(data)

    if client is None:
        __missing_mqtt()
    c = client.Client(topic)
    c.enable_logger(logger)
    if username:
        c.username_pw_set(username, password)

    c.on_connect = lambda client, userdata, flags, rc: client.subscribe(topic)
    c.on_message = on_message
    c.connect(host, port, 60)
    c.loop_forever()


def cli(
    ctx: Context,
    topic: str = Option("homie/test", "--topic", "-t", help="mqtt root/topic"),
    host: str = Option("mqtt.eclipse.org", "--mqtt-host", help="mqtt server"),
    port: int = Option(1883, "--mqtt-port", help="server port"),
    user: str = Option(
        "", "--mqtt-user", envvar="MQTT_USER", help="server username", show_default=False
    ),
    word: str = Option(
        "", "--mqtt-pass", envvar="MQTT_PASS", help="server password", show_default=False
    ),
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

    with ctx.obj["reader"] as reader:
        publish(next(reader()), metadata=True)
        for obs in reader():
            publish(obs)
