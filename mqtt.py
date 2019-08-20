#!/usr/bin/env python3

"""
Read PMS5003/PM7003/PMA003 and push measurements to MQTT server
- Homie v2.0.0 MQTT convention, partial support
  https://homieiot.github.io/specification/spec-core-v2_0_0/
"""

import time
from typing import Union, Callable, Any
import paho.mqtt.client as mqtt
import pms


def setup(
    server: str = "rpi3.local",
    username: str = "mqttuser",
    password: str = "mqttpassword",
    topic: str = "aqmon/test",
    **kwargs,
) -> Callable[[str, Union[int, str]], Any]:
    c = mqtt.Client()
    c.username_pw_set(username, password)
    c.will_set(f"{topic}/$online", "false", 1, True)
    c.on_connect = lambda client, userdata, flags, rc: client.publish(
        f"{topic}/$online", "true", 1, True
    )

    c.connect(server, 1883, 60)
    c.loop_start()
    return lambda k, v: c.publish(f"{topic}/{k}", v, 1, True)


def main(read_delay: Union[int, str] = 60, **kwargs) -> None:
    publish = setup(**kwargs)
    for k, v in {"pm01": "PM1", "pm25": "PM2.5", "pm10": "PM10"}.items():
        publish(f"{k}/$type", v)
        publish(f"{k}/$properties", "sensor,unit,concentration")
        publish(f"{k}/sensor", "PMx003")
        publish(f"{k}/unit", "ug/m3")

    for pm in pms.read(**kwargs):
        publish("pm01/concentration", pm.pm01)
        publish("pm25/concentration", pm.pm25)
        publish("pm10/concentration", pm.pm10)

        delay = int(read_delay) - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)


if __name__ == "__main__":
    import sys

    try:
        main(*sys.argv[1:])
    except KeyboardInterrupt:
        print()
