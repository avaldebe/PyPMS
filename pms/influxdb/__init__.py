"""
Read a PMS5003/PMS7003/PMSA003 sensor and push the measurements to a InfluxDB server

Notes:
- Needs Python 3.7+ for dataclasses
"""

import time
from typing import Callable, Any
from influxdb import InfluxDBClient
import pms


def setup(
    host: str, port: int, username: str, password: str, database: str, location: str
) -> Callable[[str, int], Any]:
    c = InfluxDBClient(host, port, username, password, None)
    databases = c.get_list_database()
    if len(list(filter(lambda x: x["name"] == database, databases))) == 0:
        c.create_database(database)
    c.switch_database(database)
    return lambda k, v: c.write_points(
        [{"measurement": k, "tags": {"location": location}, "fields": {"value": v}}]
    )


def main(interval: int, serial: str, **kwargs) -> None:
    publish = setup(**kwargs)

    for pm in pms.read(serial):
        publish("pm01", pm.pm01)
        publish("pm25", pm.pm25)
        publish("pm10", pm.pm10)

        delay = int(interval) - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)
