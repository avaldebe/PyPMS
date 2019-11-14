from pathlib import Path
from dataclasses import asdict
import click
from pms import logger, service, sensor


@click.group()
@click.option(
    "--sensor-model",
    "-m",
    type=click.Choice(sensor.SUPPORTED),
    help="sensor model",
    default=sensor.DEFAULT,
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
    """Read serial sensor"""
    if debug:
        logger.setLevel("DEBUG")
    ctx.obj = {"reader": sensor.SensorReader(sensor_model, serial_port, interval)}


@main.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice("csv pm num raw cf atm hcho".split()),
    help="formatted output",
    default="pm",
    show_default=True,
)
@click.pass_context
def serial(ctx, format):
    """Read sensor and print measurements"""
    with ctx.obj["reader"] as reader:
        for obs in reader():
            print(f"{obs:{format}}")


@main.command()
@click.option("--filename", "-F", help="csv formatted file", default="pms.csv", show_default=True)
@click.option("--overwrite", help="overwrite file, if already exists", is_flag=True)
@click.pass_context
def csv(ctx, filename, overwrite):
    """Read sensor and print measurements"""
    path = Path(filename)
    mode = "w" if overwrite else "a"
    logger.debug(f"open {filename} on '{mode}' mode")
    with ctx.obj["reader"] as reader, path.open(mode) as f:
        # add header to new files
        if path.stat().st_size == 0:
            obs = next(reader())
            header = ", ".join(asdict(obs).keys())
            print(header, file=f)
        for obs in reader():
            print(f"{obs:csv}", file=f)


@main.command()
@click.option(
    "--topic", "-t", type=str, help="mqtt root/topic", default="homie/test", show_default=True
)
@click.option(
    "--mqtt-host", type=str, help="mqtt server", default="mqtt.eclipse.org", show_default=True
)
@click.option("--mqtt-port", type=int, help="server port", default=1883, show_default=True)
@click.option("--mqtt-user", type=str, help="server username")
@click.option("--mqtt-pass", type=str, help="server password")
@click.pass_context
def mqtt(ctx, topic, mqtt_host, mqtt_port, mqtt_user, mqtt_pass):
    """Read sensor and push PM measurements to a MQTT server"""
    pub = service.mqtt.client_pub(
        topic=topic, host=mqtt_host, port=mqtt_port, username=mqtt_user, password=mqtt_pass
    )
    for k, v in {"pm01": "PM1", "pm25": "PM2.5", "pm10": "PM10"}.items():
        pub(
            {
                f"{k}/$type": v,
                f"{k}/$properties": "sensor,unit,concentration",
                f"{k}/sensor": ctx.obj["reader"].sensor.name,
                f"{k}/unit": "ug/m3",
            }
        )
    with ctx.obj["reader"] as reader:
        for obs in reader():
            pub({f"{k}/concentration": v for k, v in obs.subset("pm").items()})


@main.command()
@click.option("--db-host", type=str, help="database server", default="influxdb", show_default=True)
@click.option("--db-port", type=int, help="server port", default=8086, show_default=True)
@click.option("--db-user", type=str, help="server username", default="root", show_default=True)
@click.option("--db-pass", type=str, help="server password", default="root", show_default=True)
@click.option("--db-name", type=str, help="database name", default="homie", show_default=True)
@click.option(
    "--tags", type=str, help="measurement tags", default="{'location':'test'}", show_default=True
)
@click.pass_context
def influxdb(ctx, db_host, db_port, db_user, db_pass, db_name, tags):
    """Read sensor and push PM measurements to an InfluxDB server"""
    pub = service.influxdb.client_pub(
        host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name
    )
    tags = json.loads(tags)

    with ctx.obj["reader"] as reader:
        for obs in reader():
            pub(time=obs.time, tags=tags, data=obs.subset("pm"))


@main.command()
@click.option(
    "--mqtt-host", type=str, help="mqtt server", default="mqtt.eclipse.org", show_default=True
)
@click.option("--mqtt-port", type=int, help="server port", default=1883, show_default=True)
@click.option("--mqtt-user", type=str, help="server username")
@click.option("--mqtt-pass", type=str, help="server password")
@click.option("--db-host", type=str, help="database server", default="influxdb", show_default=True)
@click.option("--db-port", type=int, help="server port", default=8086, show_default=True)
@click.option("--db-user", type=str, help="server username", default="root", show_default=True)
@click.option("--db-pass", type=str, help="server password", default="root", show_default=True)
@click.option("--db-name", type=str, help="database name", default="homie", show_default=True)
def bridge(mqtt_host, mqtt_port, mqtt_user, mqtt_pass, db_host, db_port, db_user, db_pass, db_name):
    """Bridge between MQTT and InfluxDB servers"""
    pub = service.influxdb.client_pub(
        host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name
    )

    def on_sensordata(data: service.mqtt.Data) -> None:
        pub(time=data.time, tags={"location": data.location}, data={data.measurement: data.value})

    setvice.mqtt.client_sub(
        topic=topic,
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_pass,
        on_sensordata=on_sensordata,
    )
