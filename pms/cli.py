import click
from .logging import logger
from .plantower import Sensor
from .reader import PMSerial
from .mqtt import client_pub as mqtt_pub, client_sub as mqtt_sub, Data as MqttData
from .influxdb import client_pub as db_pub


@click.group()
@click.option(
    "--sensor-model",
    "-m",
    type=click.Choice([s.name for s in Sensor]),
    help="sensor model",
    default=Sensor.Default.name,
    show_default=True,
)
@click.option(
    "--serial-port",
    "-s",
    type=click.Path(),
    help="serial port",
    default="/dev/ttyUSB0",
    show_default=True,
)
@click.option(
    "--interval",
    "-i",
    type=int,
    help="seconds to wait between updates",
    default=60,
    show_default=True,
)
@click.option("--debug", is_flag=True, help="print DEBUG/logging messages")
@click.pass_context
def main(ctx, sensor_model, serial_port, interval, debug):
    """Read PMSx003 sensor"""
    if debug:
        logger.setLevel("DEBUG")
    ctx.obj = dict(sensor=PMSerial(sensor_model, serial_port, interval))


@main.command()
@click.option(
    "--format",
    "-f",
    type=str,
    help="formatted output (e.g (pm|num|cf|csv))",
    default="pm",
    show_default=True,
)
@click.pass_context
def serial(ctx, format):
    """Read sensor and print PM measurements"""
    with ctx.obj["sensor"] as sensor:
        for pm in sensor():
            print(f"{pm:{format}}")


@main.command()
@click.option(
    "--topic",
    "-t",
    type=str,
    help="mqtt root/topic",
    default="homie/test",
    show_default=True,
)
@click.option(
    "--mqtt-host",
    type=str,
    help="mqtt server",
    default="mqtt.eclipse.org",
    show_default=True,
)
@click.option(
    "--mqtt-port", type=int, help="server port", default=1883, show_default=True
)
@click.option("--mqtt-user", type=str, help="server username")
@click.option("--mqtt-pass", type=str, help="server password")
@click.pass_context
def mqtt(ctx, topic, mqtt_host, mqtt_port, mqtt_user, mqtt_pass):
    """Read sensor and push PM measurements to a MQTT server"""
    pub = mqtt_pub(
        topic=topic,
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_pass,
    )
    for k, v in {"pm01": "PM1", "pm25": "PM2.5", "pm10": "PM10"}.items():
        pub(
            {
                f"{k}/$type": v,
                f"{k}/$properties": "sensor,unit,concentration",
                f"{k}/sensor": "PMx003",
                f"{k}/unit": "ug/m3",
            }
        )
    with ctx.obj["sensor"] as sensor:
        for pm in sensor():
            pub(
                {
                    f"pm01/concentration": pm.pm01,
                    f"pm25/concentration": pm.pm25,
                    f"pm10/concentration": pm.pm10,
                }
            )


@main.command()
@click.option(
    "--db-host", type=str, help="database server", default="influxdb", show_default=True
)
@click.option(
    "--db-port", type=int, help="server port", default=8086, show_default=True
)
@click.option(
    "--db-user", type=str, help="server username", default="root", show_default=True
)
@click.option(
    "--db-pass", type=str, help="server password", default="root", show_default=True
)
@click.option(
    "--db-name", type=str, help="database name", default="homie", show_default=True
)
@click.pass_context
def influxdb(ctx, db_host, db_port, db_user, db_pass, db_name, tags):
    """Read sensor and push PM measurements to an InfluxDB server"""
    pub = db_pub(
        host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name
    )
    tags = json.loads(tags)

    with ctx.obj["sensor"] as sensor:
        for pm in sensor():
            pub(
                time=pm.time,
                tags=tags,
                data={"pm01": pm.pm01, "pm25": pm.pm25, "pm10": pm.pm10},
            )


@main.command()
@click.option(
    "--mqtt-host",
    type=str,
    help="mqtt server",
    default="mqtt.eclipse.org",
    show_default=True,
)
@click.option(
    "--mqtt-port", type=int, help="server port", default=1883, show_default=True
)
@click.option("--mqtt-user", type=str, help="server username")
@click.option("--mqtt-pass", type=str, help="server password")
@click.option(
    "--db-host", type=str, help="database server", default="influxdb", show_default=True
)
@click.option(
    "--db-port", type=int, help="server port", default=8086, show_default=True
)
@click.option(
    "--db-user", type=str, help="server username", default="root", show_default=True
)
@click.option(
    "--db-pass", type=str, help="server password", default="root", show_default=True
)
@click.option(
    "--db-name", type=str, help="database name", default="homie", show_default=True
)
def bridge(
    mqtt_host,
    mqtt_port,
    mqtt_user,
    mqtt_pass,
    db_host,
    db_port,
    db_user,
    db_pass,
    db_name,
):
    """Bridge between MQTT and InfluxDB servers"""
    pub = db_pub(
        host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name
    )

    def on_sensordata(data: MqttData) -> None:
        pub(
            time=data.time,
            tags={"location": data.location},
            data={data.measurement: data.value},
        )

    mqtt_sub(
        topic=topic,
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_pass,
        on_sensordata=on_sensordata,
    )
