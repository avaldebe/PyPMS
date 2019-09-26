from typing import Callable
from invoke import task
import pms


def main(
    *, serial: str, interval: int, fn: Callable[[pms.plantower.Data], None]
) -> None:
    try:
        with pms.PMSerial(serial) as read:
            for pm in read(interval):
                fn(pm)
    except KeyboardInterrupt:
        print()
    except Exception as e:
        pms.logger.warn(e)


@task(
    help={
        "serial": "serial port [default: /dev/ttyUSB0]",
        "interval": "seconds to wait between updates [default: 60]",
        "format": "(pm|num|csv)formatted output  [default: pm]",
    }
)
def serial(context, serial="/dev/ttyUSB0", interval=60, format="pm"):
    """Read PMSx003 sensor and print PM measurements"""
    main(serial=serial, interval=interval, fn=lambda pm: print(f"{pm:{format}}"))


@task(
    help={
        "serial": "serial port [default: /dev/ttyUSB0]",
        "interval": "seconds to wait between updates [default: 60]",
        "topic": "mqtt root/topic [default: homie/test]",
        "mqtt_host": "mqtt server [default: mqtt.eclipse.org]",
        "mqtt_port": "server port [default: 1883]",
        "mqtt_user": "server username",
        "mqtt_pass": "server password",
    }
)
def mqtt(
    context,
    serial="/dev/ttyUSB0",
    interval=60,
    topic="homie/test",
    mqtt_host="mqtt.eclipse.org",
    mqtt_port=1883,
    mqtt_user=None,
    mqtt_pass=None,
):
    """Read PMSx003 sensor and push PM measurements to a MQTT server"""
    pub = pms.mqtt.client_pub(
        topic=topic,
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_pass,
    )
    for k, v in [("pm01", "PM1"), ("pm25", "PM2.5"), ("pm10", "PM10")]:
        pub(
            {
                f"{k}/$type": v,
                f"{k}/$properties": "sensor,unit,concentration",
                f"{k}/sensor": "PMx003",
                f"{k}/unit": "ug/m3",
            }
        )

    main(
        serial,
        interval,
        lambda pm: pub(
            {
                f"pm01/concentration": pm.pm01,
                f"pm25/concentration": pm.pm25,
                f"pm10/concentration": pm.pm10,
            }
        ),
    )


@task(
    help={
        "serial": "serial port [default: /dev/ttyUSB0]",
        "interval": "seconds to wait between updates [default: 60]",
        "db_host": "database server [default: influxdb]",
        "db_port": "server port [default: 8086]",
        "db_user": "server username [default: root]",
        "db_pass": "server password [default: root]",
        "database": "database name [default: homie]",
        "tags": "measurement tags [default: {'location':'test'}]",
    }
)
def influxdb(
    context,
    serial="/dev/ttyUSB0",
    interval=60,
    db_host="influxdb",
    db_port=8086,
    db_user="root",
    db_pass="root",
    db_name="homie",
    tags="{'location':'test'}",
):
    """Read PMSx003 sensor and push PM measurements to an InfluxDB server"""
    pub = pms.influxdb.client_pub(
        host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name
    )

    main(
        serial,
        interval,
        lambda pm: pub(
            time=pm.time,
            tags=tags,
            data={"pm01": pm.pm01, "pm25": pm.pm25, "pm10": pm.pm10},
        ),
    )


@task(
    help={
        "mqtt_host": "mqtt server [default: mqtt.eclipse.org]",
        "mqtt_port": "server port [default: 1883]",
        "mqtt_user": "server username",
        "mqtt_pass": "server password",
        "db_host": "database server [default: influxdb]",
        "db_port": "server port [default: 8086]",
        "db_user": "server username [default: root]",
        "db_pass": "server password [default: root]",
        "db_name": "database name [default: homie]",
    }
)
def bridge(
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
):
    """Bridge between MQTT server/topic and InfluxDB server/database"""
    pub = pms.influxdb.client_pub(
        host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name
    )

    def on_sensordata(data: pms.mqtt.Data) -> None:
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
