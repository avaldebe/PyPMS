#!/usr/bin/env python3

"""
Read PMS5003/PM7003/PMA003 and push measurements to MQTT server
"""

import time
from typing import Union
import paho.mqtt.client as mqtt
import pms

MQTT_SERVER = "rpi3.local"
MQTT_USER = "mqttuser"
MQTT_PASSWORD = "mqttpassword"

MQTT_CLIENT_ID = "test"
MQTT_TOPIC_PMS = f"aqmon/{MQTT_CLIENT_ID}/%s/concentration"
MQTT_TOPIC_STATE = f"aqmon/{MQTT_CLIENT_ID}/$online"
MQTT_PUBLISH_DELAY = 60


def on_connect(client, userdata, flags, rc):
    client.publish(MQTT_TOPIC_STATE, "true", 1, True)


def main(read_delay: Union[int, str] = MQTT_PUBLISH_DELAY, **kwargs) -> None:
    c = mqtt.Client(MQTT_CLIENT_ID)
    c.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    c.will_set(MQTT_TOPIC_STATE, "false", 1, True)
    c.on_connect = on_connect

    c.connect(MQTT_SERVER, 1883, 60)
    c.loop_start()

    for pm in pms.read(**kwargs):
        for k, v in pm.__dict__.items():
            if k.startswith("pm"):
                c.publish(MQTT_TOPIC_PMS % k, v, 1, True)

        delay = int(read_delay) - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)


if __name__ == "__main__":
    import sys

    try:
        main(*sys.argv[1:])
    except KeyboardInterrupt:
        print()
