"""
Bridge between MQTT server/topic and InfluxDB server/database

Usage:
    pms.bridge [options]

Options:
    --MQTT_topic <topic>        MQTT root/topic [default: homie/+/+/+]
    --MQTT_host <host>          MQTT host server [default: mqtt.eclipse.org]
    --MQTT_port <port>          MQTT host port [default: 1883]
    --MQTT_user <username>      MQTT username
    --MQTT_pass <password>      MQTT password
    --InfluxDB_database <db>    InfluxDB database [default: homie]
    --InfluxDB_tags <dict>      InfluxDB measurement tags [default: {}]
    --InfluxDB_host <host>      InfluxDB host server [default: influxdb]
    --InfluxDB_port <port>      InfluxDB host port [default: 8086]
    --InfluxDB_user <username>  InfluxDB username [default: root]
    --InfluxDB_pass <password>  InfluxDB password [default: root]
    --help                      display this help and exit


NOTE:
Environment variables take precedence over command line options
- PMS_MQTT_TOPIC    overrides --MQTT_topic
- PMS_MQTT_HOST     overrides --MQTT_host
- PMS_MQTT_PORT     overrides --MQTT_port
- PMS_MQTT_USER     overrides --MQTT_user
- PMS_MQTT_PASS     overrides --MQTT_pass
- PMS_INFLUX_DB     overrides --InfluxDB_database
- PMS_INFLUX_TAGS   overrides --InfluxDB_tags
- PMS_INFLUX_HOST   overrides --InfluxDB_host
- PMS_INFLUX_PORT   overrides --InfluxDB_port
- PMS_INFLUX_USER   overrides --InfluxDB_user
- PMS_INFLUX_PASS   overrides --InfluxDB_pass
"""

import re
from typing import Dict, List, Optional, Union, Any, NamedTuple
from datetime import datetime
from docopt import docopt
from pms.mqtt import parse_args as mqtt_args, client as mqtt_client
from pms.influxdb import (
    parse_args as influxdb_args,
    client as influxdb_client,
    pub as influxdb_pub,
)


def parse_args(args: Dict[str, str]) -> Dict[str, Any]:
    """Extract options from docopt output"""

    def get_opts(start: str) -> Dict[str, str]:
        """Extract MQTT/InfluxDB keywords"""
        d = {k.replace(start, "--"): v for k, v in args.items() if k.startswith(start)}
        d.update({"--serial": "/dev/null", "--interval": "0"})  # dummy values
        return d

    return dict(
        mqtt=mqtt_args(get_opts("--MQTT_")),
        influxdb=influxdb_args(get_opts("--InfluxDB_")),
    )


class SensorData(NamedTuple):
    location: str
    measurement: str
    value: float
    time: int

    @staticmethod
    def now() -> int:
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())


def _parse_mqtt_message(topic: str, payload: str) -> Optional[SensorData]:
    time = SensorData.now()
    match = re.match(r"home/([^/]+)/([^/]+)/([^/]+)", topic)
    if not match:
        return None

    location = match.group(1)
    measurement = match.group(2)
    if measurement.startswith("$"):
        return None

    try:
        value = float(payload)
    except ValueError:
        return None
    return SensorData(location, measurement, value, time)


def _publish_sensor_data(client, obs: Optional[SensorData] = None) -> None:
    if not obs:
        return
    influxdb_pub(
        client, {"location": obs.location}, obs.time, {obs.measurement: obs.value}
    )


def main(mqtt: Dict[str, Any], influxdb: Dict[str, Any]) -> None:
    influxdb = influxdb_client(**influxdb)

    def decode_msg_from_topic(topic: str, payload: str) -> None:
        _publish_sensor_data(influxdb, _parse_mqtt_message(topic, payload))

    mqtt_client(decode_msg_from_topic=decode_msg_from_topic, **mqtt)


def cli(argv: Optional[List[str]] = None) -> None:
    args = parse_args(docopt(__doc__, argv))
    exit(args)
    main(**args)


if __name__ == "__main__":
    cli()
