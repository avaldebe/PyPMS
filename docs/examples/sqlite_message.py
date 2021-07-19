#!/usr/bin/env python3
"""
Read raw messages from 2 different sensors and store them on a sqlite DB.
After reading the sensor, decode all messages on DB and print them.

- PMSx003 senor on /dev/ttyUSB0
- MCU680 sensor on /dev/ttyUSB1
- read 4 samples for each sensor, by default
- read one sample from each sensor every 20 seconds, by default

NOTE:
When reading 2 or more sensors only the timing of the first sensor is guarantied.
In this example, the second sensor will be read right after the first sensor.
"""

import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Callable, ContextManager, Generator

from typer import Argument, Option, progressbar

from pms.core import Sensor, SensorReader
from pms.core.reader import ObsData, RawData


def main(
    db_path: Path = Argument(Path("pypms.sqlite"), help="sensor messages DB"),
    samples: int = Option(4, "--samples", "-n"),
    interval: int = Option(20, "--interval", "-i"),
):
    """
    Read raw messages from 2 different sensors
    (PMSx003 on /dev/ttyUSB0 and MCU680 on /dev/ttyUSB1)
    and store them on a sqlite DB.

    After reading the sensor, decode all messages on DB and print them.
    """

    # get DB context manager
    message_db = pypms_db(db_path)

    reader = dict(
        pms=SensorReader("PMSx003", "/dev/ttyUSB0", interval, samples),
        bme=SensorReader("MCU680", "/dev/ttyUSB1", interval, samples),
    )

    # read from each sensor and write to DB
    with message_db() as db, reader["pms"] as pms, reader["bme"] as bme:
        # read one obs from each sensor at the time
        with progressbar(
            zip(pms(raw=True), bme(raw=True)), length=samples, label="reading sensors"
        ) as progress:
            for pms_obs, env_obs in progress:
                write_message(db, pms.sensor, pms_obs)
                write_message(db, bme.sensor, env_obs)

    # read and decode all messages on the DB
    with message_db() as db:
        # extract obs from one sensor at the time
        for sensor in [r.sensor for r in reader.values()]:
            print(sensor)
            for obs in read_obs(db, sensor):
                print(obs)


def pypms_db(db_path: Path) -> Callable[[], ContextManager[sqlite3.Connection]]:
    """
    create db and messages table, if do not exists already
    and return a context manager for a DB connection
    """

    @contextmanager
    def connect() -> Generator[sqlite3.Connection, None, None]:
        db = sqlite3.connect(str(db_path))
        try:
            yield db
        except sqlite3.Error as e:
            exit(e)
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


def read_obs(db: sqlite3.Connection, sensor: Sensor) -> Generator[ObsData, None, None]:
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
    decode = lambda row: sensor.decode(row[0], time=row[1])
    with closing(db.cursor()) as cur:
        cur.execute(select, (sensor.name,))
        return (decode(row) for row in cur.fetchall())


if __name__ == "__main__":
    from typer import run

    try:
        run(main)
    except KeyboardInterrupt:
        print("")
