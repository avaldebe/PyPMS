"""
Read a PMS5003/PMS7003/PMSA003 sensor and push PM measurements to an InfluxDB server

Usage:
    pms influxdb [options]

Options:
    -d, --database <db>     InfluxDB database [default: homie]
    -t, --tags <dict>       InfluxDB measurement tags [default: {"location":"test"}]
    -h, --host <host>       InfluxDB host server [default: influxdb]
    -p, --port <port>       InfluxDB host port [default: 8086]
    -u, --user <username>   InfluxDB username [default: root]
    -P, --pass <password>   InfluxDB password [default: root]

Other:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --help                  display this help and exit

NOTE:
Environment variables take precedence over command line options
- PMS_INFLUX_DB     overrides -d, --database
- PMS_INFLUX_TAGS   overrides -t, --tags
- PMS_INFLUX_HOST   overrides -h, --host
- PMS_INFLUX_PORT   overrides -p, --port
- PMS_INFLUX_USER   overrides -u, --user
- PMS_INFLUX_PASS   overrides -P, --pass
- PMS_INTERVAL      overrides -n, --interval
- PMS_SERIAL        overrides -s, --serial
"""

import os
import time
from typing import Dict, List, Optional, Union, Any
import json
from docopt import docopt
from influxdb import InfluxDBClient
from pms import read


def parse_args(args: Dict[str, str]) -> Dict[str, Any]:
    return dict(
        interval=int(os.environ.get("PMS_INTERVAL", args["--interval"])),
        serial=os.environ.get("PMS_SERIAL", args["--serial"]),
        tags=json.loads(os.environ.get("PMS_INFLUX_TAGS", args["--tags"])),
        host=os.environ.get("PMS_INFLUX_HOST", args["--host"]),
        port=int(os.environ.get("PMS_INFLUX_PORT", args["--port"])),
        username=os.environ.get("PMS_INFLUX_USER", args["--user"]),
        password=os.environ.get("PMS_INFLUX_PASS", args["--pass"]),
        db_name=os.environ.get("PMS_INFLUX_DB", args["--database"]),
    )


def setup(
    host: str, port: int, username: str, password: str, db_name: str
) -> InfluxDBClient:
    c = InfluxDBClient(host, port, username, password, None)
    databases = c.get_list_database()
    if len(list(filter(lambda x: x["name"] == db_name, databases))) == 0:
        c.create_database(db_name)
    c.switch_database(db_name)
    return c


def pub(
    client: InfluxDBClient, tags: Dict[str, str], time: str, data: Dict[str, int]
) -> None:
    client.write_points(
        [
            {"measurement": k, "tags": tags, "time": time, "fields": {"value": v}}
            for k, v in data.items()
        ]
    )


def main(interval: int, serial: str, tags: Dict[str, str], **kwargs) -> None:
    """
    TODO: check pm.timestamp("%FT%TZ") actually returns UTC time
    """
    client = setup(**kwargs)

    for pm in read(serial):
        pub(
            client,
            tags,
            pm.timestamp("%FT%TZ"),
            {"pm01": pm.pm01, "pm25": pm.pm25, "pm10": pm.pm10},
        )

        delay = interval - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)


def cli(argv: Optional[List[str]] = None) -> None:
    args = parse_args(docopt(__doc__, argv))
    main(**args)
