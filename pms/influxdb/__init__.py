"""
Read a PMS5003/PMS7003/PMSA003 sensor and push the measurements to a InfluxDB server
"""

import time
from typing import Dict
from influxdb import InfluxDBClient
import pms


def setup(
    host: str, port: int, username: str, password: str, db_name: str
) -> InfluxDBClient:
    c = InfluxDBClient(host, port, username, password, None)
    databases = c.get_list_database()
    if len(list(filter(lambda x: x["name"] == db_name, databases))) == 0:
        c.create_database(db_name)
    c.switch_database(db_name)
    return c


def pub(client: InfluxDBClient, tags: Dict, time: str, data: Dict) -> None:
    client.write_points(
        [
            {"measurement": k, "tags": tags, "time": time, "fields": {"value": v}}
            for k, v in data.items()
        ]
    )


def main(interval: int, serial: str, location: str, **kwargs) -> None:
    client = setup(**kwargs)

    for pm in pms.read(serial):
        pub(
            client,
            {"location": location},
            pm.timestamp("%FT%TZ"),
            {"pm01": pm.pm01, "pm25": pm.pm25, "pm10": pm.pm10},
        )

        delay = int(interval) - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)
