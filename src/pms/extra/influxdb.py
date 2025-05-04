from __future__ import annotations

import json
from dataclasses import fields
from typing import Annotated, Protocol

import typer
from influxdb import InfluxDBClient as Client

from pms.core import exit_on_fail


class PubFunction(Protocol):
    def __call__(self, *, time: int, tags: dict[str, str], data: dict[str, float]) -> None: ...


def client_pub(*, host: str, port: int, username: str, password: str, db_name: str) -> PubFunction:
    c = Client(host, port, username, password, None)
    if db_name not in {x["name"] for x in c.get_list_database()}:
        c.create_database(db_name)
    c.switch_database(db_name)

    def pub(*, time: int, tags: dict[str, str], data: dict[str, float]) -> None:
        c.write_points(
            [
                {"measurement": k, "tags": tags, "time": time, "fields": {"value": v}}
                for k, v in data.items()
            ],
            time_precision="s",
        )

    return pub


def cli(
    ctx: typer.Context,
    host: Annotated[str, typer.Option("--db-host", help="database server")] = "influxdb",
    port: Annotated[int, typer.Option("--db-port", help="server port")] = 8086,
    user: Annotated[
        str, typer.Option("--db-user", envvar="DB_USER", help="server username")
    ] = "root",
    word: Annotated[
        str, typer.Option("--db-pass", envvar="DB_PASS", help="server password")
    ] = "root",
    name: Annotated[str, typer.Option("--db-name", help="database name")] = "homie",
    jtag: Annotated[str, typer.Option("--tags", help="measurement tags")] = json.dumps(
        {"location": "test"}
    ),
):
    """Read sensor and push PM measurements to an InfluxDB server"""
    pub = client_pub(host=host, port=port, username=user, password=word, db_name=name)
    tags = json.loads(jtag.replace("'", '"'))

    with exit_on_fail(ctx.obj["reader"]) as reader:
        for obs in reader():
            data = {field.name: getattr(obs, field.name) for field in fields(obs) if field.metadata}
            pub(time=obs.time, tags=tags, data=data)
