import os, json
from typing import Dict, List, Optional, Any, Callable
from mypy_extensions import NamedArg
from influxdb import InfluxDBClient
from invoke import task
from pms import PMSerial


def client_pub(
    *, host: str, port: int, username: str, password: str, db_name: str
) -> Callable[
    [
        NamedArg(int, "time"),
        NamedArg(Dict[str, str], "tags"),
        NamedArg(Dict[str, float], "data"),
    ],
    None,
]:
    c = InfluxDBClient(host, port, username, password, None)
    databases = c.get_list_database()
    if len(list(filter(lambda x: x["name"] == db_name, databases))) == 0:
        c.create_database(db_name)
    c.switch_database(db_name)

    def pub(*, time: int, tags: Dict[str, str], data: Dict[str, float]) -> None:
        c.write_points(
            [
                {"measurement": k, "tags": tags, "time": time, "fields": {"value": v}}
                for k, v in data.items()
            ],
            time_precision="s",
        )

    return pub


@task(
    name="influxdb",
    help={
        "serial": "serial port [default: /dev/ttyUSB0]",
        "interval": "seconds to wait between updates [default: 60]",
        "db-host": "database server [default: influxdb]",
        "db-port": "server port [default: 8086]",
        "db-user": "server username [default: root]",
        "db-pass": "server password [default: root]",
        "db-name": "database name [default: homie]",
        "tags": "measurement tags [default: {'location':'test'}]",
        "debug": "print DEBUG/logging messages",
    },
)
def main(
    context,
    serial="/dev/ttyUSB0",
    interval=60,
    db_host="influxdb",
    db_port=8086,
    db_user="root",
    db_pass="root",
    db_name="homie",
    tags="{'location':'test'}",
    debug=False,
):
    """Read PMSx003 sensor and push PM measurements to an InfluxDB server"""
    if debug:
        logger.setLevel("DEBUG")
    try:
        pub = client_pub(
            host=db_host,
            port=db_port,
            username=db_user,
            password=db_pass,
            db_name=db_name,
        )
        tags = json.loads(tags)

        with PMSerial(serial) as read:
            for pm in read(interval):
                pub(
                    time=pm.time,
                    tags=tags,
                    data={"pm01": pm.pm01, "pm25": pm.pm25, "pm10": pm.pm10},
                )
    except KeyboardInterrupt:
        print()
    except Exception as e:
        logger.exception(e)
