#!/usr/bin/env python3
"""
Read raw messages from a supported sensor and store them on a sqlite DB.
After reading the sensor, decode all messages on DB and print them.

- PMSx003 senor on /dev/ttyUSB0 by default
- read 4 samples for each sensor, by default
- read one sample from each sensor every 20 seconds, by default
"""

import sqlite3
from collections.abc import Iterator
from contextlib import AbstractContextManager, closing, contextmanager
from pathlib import Path
from typing import Annotated, Callable

import typer

from pms.core import Sensor, SensorReader, Supported
from pms.core.reader import RawData
from pms.core.types import ObsData

app = typer.Typer(add_completion=False)


@app.command()
def main(
    model: Annotated[Supported, typer.Argument(help="sensor model")],
    port: Annotated[str, typer.Argument(help="serial port")] = "/dev/ttyUSB0",
    db_path: Annotated[Path, typer.Argument(help="sensor messages DB")] = Path("pypms.sqlite"),
    samples: Annotated[int, typer.Option("--samples", "-n", min=1)] = 4,
    interval: Annotated[int, typer.Option("--interval", "-i", min=0)] = 20,
):
    """
    Read raw messages from a supported sensor and store them on a sqlite DB.
    After reading the sensor, decode all messages on DB and print them.
    """

    # get DB context manager
    message_db = pypms_db(db_path)
    sensor = Sensor[model]

    # read from sensor and write to DB
    progress: Iterator[RawData]
    msg: RawData
    with message_db() as db, SensorReader(sensor, port, interval, samples) as reader:
        # read one obs from each sensor at the time
        with typer.progressbar(
            reader(raw=True), length=samples, label=f"reading {sensor}"
        ) as progress:
            for msg in progress:
                write_message(db, sensor, msg)

    # read and decode all `sensor` messages on the DB
    with message_db() as db:
        print(sensor)
        for obs in read_obs(db, sensor):
            print(obs)


def pypms_db(db_path: Path) -> Callable[[], AbstractContextManager[sqlite3.Connection]]:
    """
    create db and messages table, if do not exists already
    and return a context manager for a DB connection
    """

    @contextmanager
    def connect() -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(str(db_path))
        try:
            yield db
        except sqlite3.Error as e:
            exit(str(e))
        finally:
            db.close()

    create_table = """
        CREATE TABLE IF NOT EXISTS messages (
            time DATETIME NOT NULL,
            sensor TEXT NOT NULL,
            message BLOB NOT NULL,
            UNIQUE (time, sensor)
        );
        """
    with connect() as db, db, closing(db.cursor()) as cur:
        cur.executescript(create_table)

    return connect


def write_message(db: sqlite3.Connection, sensor: Sensor, message: RawData):
    """insert raw messages into the DB"""

    insert = """
        INSERT OR IGNORE INTO messages (time, sensor, message)
        VALUES (?, ?, ?);
        """
    with db, closing(db.cursor()) as cur:
        cur.execute(insert, (message.time, sensor.name, message.data))


def read_obs(db: sqlite3.Connection, sensor: Sensor) -> Iterator[ObsData]:
    """read messages from DB and return decoded observations"""

    select = """
        SELECT
            message, time
        FROM
            messages
        WHERE
            sensor IS ?
        ORDER BY
            time;
        """

    def decode(row):
        return sensor.decode(row[0], time=row[1])

    with closing(db.cursor()) as cur:
        cur.execute(select, (sensor.name,))
        return (decode(row) for row in cur.fetchall())


if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        print("")
