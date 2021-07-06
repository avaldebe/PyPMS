import json
import sys
from dataclasses import fields
from typing import Dict

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Protocol
else:  # pragma: no cover
    from typing_extensions import Protocol

from typer import Abort, Context, Option, colors, echo, style

try:
    from influxdb import InfluxDBClient as client  # type: ignore
except ModuleNotFoundError:
    client = None  # type: ignore


def __missing_influxdb():  # pragma: no cover
    name = style(__name__, fg=colors.GREEN, bold=True)
    package = style("pypms", fg=colors.GREEN, bold=True)
    module = style("influxdb", fg=colors.RED, bold=True)
    extra = style("influxdb", fg=colors.RED, bold=True)
    pip = style("python3 -m pip install --upgrade", fg=colors.GREEN)
    pipx = style("pipx inject", fg=colors.GREEN)
    echo(
        f"""
{name} provides additional functionality to {package}.
This functionality requires the {module} module, which is not installed.
You can install this additional dependency with
\t{pip} {package}[{extra}]
Or, if you installed {package} with pipx
\t{pipx} {package} {module}
"""
    )
    raise Abort()


class PubFunction(Protocol):  # pragma: no cover
    def __call__(self, *, time: int, tags: Dict[str, str], data: Dict[str, float]) -> None:
        ...


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

    def pub(*, time: int, tags: Dict[str, str], data: Dict[str, float]) -> None:
        c.write_points(
            [
                {"measurement": k, "tags": tags, "time": time, "fields": {"value": v}}
                for k, v in data.items()
            ],
            time_precision="s",
        )

    return pub


def cli(
    ctx: Context,
    host: str = Option("influxdb", "--db-host", help="database server"),
    port: int = Option(8086, "--db-port", help="server port"),
    user: str = Option("root", "--db-user", envvar="DB_USER", help="server username"),
    word: str = Option("root", "--db-pass", envvar="DB_PASS", help="server password"),
    name: str = Option("homie", "--db-name", help="database name"),
    jtag: str = Option(json.dumps({"location": "test"}), "--tags", help="measurement tags"),
):
    """Read sensor and push PM measurements to an InfluxDB server"""
    pub = client_pub(host=host, port=port, username=user, password=word, db_name=name)
    tags = json.loads(jtag.replace("'", '"'))

    with ctx.obj["reader"] as reader:
        for obs in reader():
            data = {field.name: getattr(obs, field.name) for field in fields(obs) if field.metadata}
            pub(time=obs.time, tags=tags, data=data)
