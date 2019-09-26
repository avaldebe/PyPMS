from typing import Dict, List, Optional, Union, Any
from invoke import task
from pms import logger, mqtt, influxdb


@task(
    name="bridge",
    help={
        "mqtt-host": "mqtt server [default: mqtt.eclipse.org]",
        "mqtt-port": "server port [default: 1883]",
        "mqtt-user": "server username",
        "mqtt-pass": "server password",
        "db-host": "database server [default: influxdb]",
        "db-port": "server port [default: 8086]",
        "db-user": "server username [default: root]",
        "db-pass": "server password [default: root]",
        "db-name": "database name [default: homie]",
        "debug": "print DEBUG/logging messages",
    },
)
def main(
    context,
    mqtt_host="mqtt.eclipse.org",
    mqtt_port=1883,
    mqtt_user=None,
    mqtt_pass=None,
    db_host="influxdb",
    db_port=8086,
    db_user="root",
    db_pass="root",
    db_name="homie",
    debug=False,
):
    """Bridge between MQTT server/topic and InfluxDB server/database"""
    if debug:
        logger.setLevel("DEBUG")
    try:
        pub = influxdb.client_pub(
            host=db_host,
            port=db_port,
            username=db_user,
            password=db_pass,
            db_name=db_name,
        )

        def on_sensordata(data: mqtt.Data) -> None:
            pub(
                time=data.time,
                tags={"location": data.location},
                data={data.measurement: data.value},
            )

        mqtt.client_sub(
            topic=topic,
            host=mqtt_host,
            port=mqtt_port,
            username=mqtt_user,
            password=mqtt_pass,
            on_sensordata=on_sensordata,
        )
    except KeyboardInterrupt:
        print()
    except Exception as e:
        logger.warn(e)
