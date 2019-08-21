"""
Read a PMS5003/PMS7003/PMSA003 sensor and push the measurements to a MQTT server

Notes:
- Only partial support for Homie v2.0.0 MQTT convention 
  https://homieiot.github.io/specification/spec-core-v2_0_0/
"""

import time
from typing import Dict
from paho.mqtt import publish
import pms


def pub(
    data: Dict, root: str, host: str, port: int, username: str, password: str
) -> None:
    mesages = [(f"{root}/{k}", v, 1, True) for k, v in data.items()]
    will = {"topic": f"{root}/$online", "payload": "false", "qos": 1, "retain": True}
    auth = {"username": username, "password": password} if username else None
    publish.multiple(mesages, hostname=host, port=port, will=will, auth=auth)


def main(interval: int, serial: str, **kwargs) -> None:
    for k, v in [("pm01", "PM1"), ("pm25", "PM2.5"), ("pm10", "PM10")]:
        pub(
            {
                f"{k}/$type": v,
                f"{k}/$properties": "sensor,unit,concentration",
                f"{k}/sensor": "PMx003",
                f"{k}/unit": "ug/m3",
            },
            **kwargs,
        )
    for pm in pms.read(serial):
        pub(
            {
                "pm01/concentration": pm.pm01,
                "pm25/concentration": pm.pm25,
                "pm10/concentration": pm.pm10,
            },
            **kwargs,
        )

        delay = int(interval) - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)
