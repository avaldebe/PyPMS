from __future__ import annotations

from typing import Protocol

from influxdb import InfluxDBClient as Client


class Publisher(Protocol):
    def __call__(self, *, time: int, tags: dict[str, str], data: dict[str, float]) -> None: ...


def publisher(*, host: str, port: int, username: str, password: str, db_name: str) -> Publisher:
    """returns a function to publish to `db_name` at `host`"""
    c = Client(host, port, username, password, None)
    if db_name not in {x["name"] for x in c.get_list_database()}:
        c.create_database(db_name)
    c.switch_database(db_name)

    def pub(*, time: int, tags: dict[str, str], data: dict[str, float]) -> None:
        """publisg to DB"""
        c.write_points(
            [
                {"measurement": k, "tags": tags, "time": time, "fields": {"value": v}}
                for k, v in data.items()
            ],
            time_precision="s",
        )

    return pub
