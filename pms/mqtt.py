"""
Read a PMSx003 sensor and push PM measurements to a MQTT server

Usage:
    pms mqtt [options]

Options:
    -t, --topic <topic>     MQTT root/topic [default: homie/test]
    -h, --host <host>       MQTT host server [default: mqtt.eclipse.org]
    -p, --port <port>       MQTT host port [default: 1883]
    -u, --user <username>   MQTT username
    -P, --pass <password>   MQTT password

Other:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --help                  display this help and exit

NOTE:
Environment variables take precedence over command line options
- PMS_MQTT_TOPIC    overrides -t, --topic
- PMS_MQTT_HOST     overrides -h, --host
- PMS_MQTT_PORT     overrides -p, --port
- PMS_MQTT_USER     overrides -u, --user
- PMS_MQTT_PASS     overrides -P, --pass
- PMS_INTERVAL      overrides -n, --interval
- PMS_SERIAL        overrides -s, --serial

NOTE:
Only partial support for Homie v2.0.0 MQTT convention
https://homieiot.github.io/specification/spec-core-v2_0_0/
"""

import os
from datetime import datetime
import time
from typing import Dict, List, Optional, Union, Any, Callable, NamedTuple
import paho.mqtt.client as mqtt
from docopt import docopt
from pms import read, logger


def parse_args(args: Dict[str, str]) -> Dict[str, Any]:
    """Extract options from docopt output"""
    return dict(
        interval=int(os.environ.get("PMS_INTERVAL", args["--interval"])),
        serial=os.environ.get("PMS_SERIAL", args["--serial"]),
        host=os.environ.get("PMS_MQTT_HOST", args["--host"]),
        port=int(os.environ.get("PMS_MQTT_PORT", args["--port"])),
        username=os.environ.get("PMS_MQTT_USER", args["--user"]),
        password=os.environ.get("PMS_MQTT_PASS", args["--pass"]),
        topic=os.environ.get("PMS_MQTT_TOPIC", args["--topic"]),
    )


def client_pub(
    topic: str, host: str, port: int, username: str, password: str
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


class SensorData(NamedTuple):
    time: int
    location: str
    measurement: str
    value: float

    @staticmethod
    def now() -> int:
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())

    @classmethod
    def decode(
        cls, topic: str, payload: str, *, time: Optional[int] = None
    ) -> "SensorData":
        """Decode a MQTT message
        
        For example
        >>> decode("homie/test/pm10/concentration", "27")
        >>> SensorData(now(), "test", "pm10", 27)
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


def pub(client: mqtt.Client, data: Dict[str, Union[int, str]]) -> None:
    for k, v in data.items():
        client.publish(k, v, 1, True)


def main(interval: int, serial: str, **kwargs) -> None:
    pub = client_pub(**kwargs)

    for k, v in [("pm01", "PM1"), ("pm25", "PM2.5"), ("pm10", "PM10")]:
        pub(
            {
                f"{k}/$type": v,
                f"{k}/$properties": "sensor,unit,concentration",
                f"{k}/sensor": "PMx003",
                f"{k}/unit": "ug/m3",
            }
        )

    for pm in read(serial):
        pub(
            {
                f"pm01/concentration": pm.pm01,
                f"pm25/concentration": pm.pm25,
                f"pm10/concentration": pm.pm10,
            }
        )

        delay = interval - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)


def cli(argv: Optional[List[str]] = None) -> None:
    args = parse_args(docopt(__doc__, argv))
    main(**args)
