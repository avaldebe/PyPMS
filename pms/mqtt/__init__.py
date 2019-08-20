"""
Read a PMS5003/PMS7003/PMSA003 sensor and push the measurements to a MQTT server

Notes:
- Needs Python 3.7+ for dataclasses
- Only partial support for Homie v2.0.0 MQTT convention 
  https://homieiot.github.io/specification/spec-core-v2_0_0/
"""

import time
from typing import Union, Callable, Any
import paho.mqtt.client as mqtt
import pms


def setup(
    host: str, port: int, username: str, password: str, topic: str
) -> Callable[[str, Union[int, str]], Any]:
    c = mqtt.Client()
    if username:
        c.username_pw_set(username, password)
    c.will_set(f"{topic}/$online", "false", 1, True)
    c.on_connect = lambda client, userdata, flags, rc: client.publish(
        f"{topic}/$online", "true", 1, True
    )

    c.connect(host, 1883, 60)
    c.loop_start()
    return lambda k, v: c.publish(f"{topic}/{k}", v, 1, True)


def main(interval: int, serial: str, **kwargs) -> None:
    publish = setup(**kwargs)
    for k, v in [("pm01", "PM1"), ("pm25", "PM2.5"), ("pm10", "PM10")]:
        publish(f"{k}/$type", v)
        publish(f"{k}/$properties", "sensor,unit,concentration")
        publish(f"{k}/sensor", "PMx003")
        publish(f"{k}/unit", "ug/m3")

    for pm in pms.read(serial):
        publish("pm01/concentration", pm.pm01)
        publish("pm25/concentration", pm.pm25)
        publish("pm10/concentration", pm.pm10)

        delay = int(interval) - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)
