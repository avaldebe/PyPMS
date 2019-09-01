"""
Read a PMS5003/PMS7003/PMSA003 sensor and push PM measurements to an InfluxDB server

Usage:
    pms.influxdb [options]

Options:
    --location <tag>        InfluxDB location tag [default: test]
    --database <db>         InfluxDB database [default: homie]
    --host <host>           InfluxDB host server [default: influxdb]
    --port <port>           InfluxDB host port [default: 8086]
    --user <username>       InfluxDB username [default: root]
    --pass <password>       InfluxDB password [default: root]

Other:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --help                  display this help and exit
"""

import time
from typing import Dict, Union, Any
from influxdb import InfluxDBClient
import pms


def parse_args(args: Dict[str, str]) -> Dict[str, Any]:
    return dict(
        interval=int(args["--interval"]),
        serial=args["--serial"],
        location=args["--location"],
        host=args["--host"],
        port=int(args["--port"]),
        username=args["--user"],
        password=args["--pass"],
        db_name=args["--database"],
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


if __name__ == "__main__":
    from docopt import docopt

    args = parse_args(docopt(__doc__))
    try:
        main(**args)
    except KeyboardInterrupt:
        print()
    except Exception as e:
        pms.logger.exception(e)
