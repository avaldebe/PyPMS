import os, json
from typing import Dict, List, Optional, Any, Callable
from mypy_extensions import NamedArg
from influxdb import InfluxDBClient


def client_pub(
    *, host: str, port: int, username: str, password: str, db_name: str
) -> Callable[
    [NamedArg(int, "time"), NamedArg(Dict[str, str], "tags"), NamedArg(Dict[str, float], "data")],
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
