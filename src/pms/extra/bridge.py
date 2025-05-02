from typing import Annotated

import typer

from .influxdb import client_pub
from .mqtt import Data, client_sub


def cli(
    mqtt_topic: Annotated[str, typer.Option(help="mqtt root/topic")] = "homie/+/+/+",
    mqtt_host: Annotated[str, typer.Option(help="mqtt server")] = "mqtt.eclipse.org",
    mqtt_port: Annotated[int, typer.Option(help="server port")] = 1883,
    mqtt_user: Annotated[
        str, typer.Option(envvar="MQTT_USER", help="server username", show_default=False)
    ] = "",
    mqtt_pass: Annotated[
        str, typer.Option(envvar="MQTT_PASS", help="server password", show_default=False)
    ] = "",
    db_host: Annotated[str, typer.Option(help="database server")] = "influxdb",
    db_port: Annotated[int, typer.Option(help="server port")] = 8086,
    db_user: Annotated[str, typer.Option(envvar="DB_USER", help="server username")] = "root",
    db_pass: Annotated[str, typer.Option(envvar="DB_PASS", help="server password")] = "root",
    db_name: Annotated[str, typer.Option(help="database name")] = "homie",
):
    """Bridge between MQTT and InfluxDB servers"""
    pub = client_pub(
        host=db_host, port=db_port, username=db_user, password=db_pass, db_name=db_name
    )

    def on_sensordata(data: Data) -> None:
        pub(time=data.time, tags={"location": data.location}, data={data.measurement: data.value})

    client_sub(
        topic=mqtt_topic,
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_pass,
        on_sensordata=on_sensordata,
    )
