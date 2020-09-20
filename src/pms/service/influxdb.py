import os
import json
from dataclasses import fields
from typing import Dict, Callable
from mypy_extensions import NamedArg
from influxdb import InfluxDBClient
from typer import Context, Option
from ..sensor.base import ObsData


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


def influxdb(
    ctx: Context,
    host: str = Option("influxdb", "--db-host", help="database server"),
    port: int = Option(8086, "--db-port", help="server port"),
    user: str = Option("root", "--db-user", help="server username"),
    word: str = Option("root", "--db-pass", help="server password"),
    name: str = Option("homie", "--db-name", help="database name"),
    jtag: str = Option("{'location':'test'}", "--tags", help="measurement tags"),
):
    """Read sensor and push PM measurements to an InfluxDB server"""
    pub = client_pub(host=host, port=port, username=user, password=word, db_name=name)
    tags = json.loads(jtag)

    with ctx.obj["reader"] as reader:
        for obs in reader():
            data = {field.name: getattr(obs, field.name) for field in fields(obs) if field.metadata}
            pub(time=obs.time, tags=tags, data=data)
