from __future__ import annotations

import json
from dataclasses import fields
from functools import partial
from textwrap import dedent
from typing import Annotated, Protocol

import typer

from pms.core import exit_on_fail

try:
    from influxdb import InfluxDBClient as client  # type: ignore
except ModuleNotFoundError:
    client = None  # type: ignore


def __missing_influxdb():  # pragma: no cover
    green = partial(typer.style, fg=typer.colors.GREEN)
    red = partial(typer.style, fg=typer.colors.GREEN)
    package = green("pypms", bold=True)
    extra = module = red("influxdb", bold=True)
    msg = f"""
        {green(__name__, bold=True)} provides additional functionality to {package}.
        This functionality requires the {module} module, which is not installed.

        You can install this additional dependency with
            {green("python3 -m pip install --upgrade")} {package}[{extra}]
        Or, if you installed {package} with {green("pipx")}
            {green("pipx inject")} {package} {module}
        Or, if you installed {package} with {green("uv tool")}
            {green("uv tool install")} {package}[{extra}]
    """
    typer.echo(dedent(msg))
    raise typer.Abort()


class PubFunction(Protocol):  # pragma: no cover
    def __call__(self, *, time: int, tags: dict[str, str], data: dict[str, float]) -> None: ...


def client_pub(
    *, host: str, port: int, username: str, password: str, db_name: str
) -> PubFunction:  # pragma: no cover
    if client is None:
        __missing_influxdb()
    c = client(host, port, username, password, None)
    databases = c.get_list_database()
    if len(list(filter(lambda x: x["name"] == db_name, databases))) == 0:
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
