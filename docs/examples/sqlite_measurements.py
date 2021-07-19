#!/usr/bin/env python3
"""
Read measurements from 2 different sensors and store them
on a sqlite DB as a "tall table" with a "wide table" view for each sensor.
After reading the sensor, get all measurements from the DB amd print them by sensor.

- PMSx003 senor on /dev/ttyUSB0
- MCU680 sensor on /dev/ttyUSB1
- read 4 samples for each sensor, by default
- read one sample from each sensor every 20 seconds, by default

NOTE:
the read_obs function creates a subclass of sensor.Data in order to avoid the
callin to __post_init__, as this was already tone when the sensor message was decoded.
Please open an issue or submit a PR i you know of a cleaner way to achieve this.
"""

import sqlite3
from contextlib import closing, contextmanager
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Callable, ContextManager, Generator

from typer import Argument, Option, progressbar

from pms.core import Sensor, SensorReader
from pms.core.reader import ObsData


def main(
    db_path: Path = Argument(Path("pypms.sqlite"), help="sensor measurements DB"),
    samples: int = Option(4, "--samples", "-n"),
    interval: int = Option(20, "--interval", "-i"),
):
    """
    Read measurements from 2 different sensors
    (PMSx003 on /dev/ttyUSB0 and MCU680 on /dev/ttyUSB1)
    and store them on a sqlite DB as a "tall table" with a "wide table" view for each sensor.

    After reading the sensors, get all measurements from the DB amd print them by sensor.
    """

    # get DB context manager
    measurements_db = pypms_db(db_path)

    reader = dict(
        pms=SensorReader("PMSx003", "/dev/ttyUSB0", interval, samples),
        bme=SensorReader("MCU680", "/dev/ttyUSB1", interval, samples),
    )

    # read from each sensor and write to DB
    with measurements_db() as db, reader["pms"] as pms, reader["bme"] as bme:
        # read one obs from each sensor at the time
        with progressbar(zip(pms(), bme()), length=samples, label="reading sensors") as progress:
            for pms_obs, env_obs in progress:
                write_measurements(db, pms.sensor, pms_obs)
                write_measurements(db, bme.sensor, env_obs)

    # read all measurements on the DB and reconstruct sensor.Data objects
    with measurements_db() as db:
        # extract obs from one sensor at the time
        for sensor in [r.sensor for r in reader.values()]:
            print(sensor)
            for obs in read_obs(db, sensor):
                print(obs)


def pypms_db(db_path: Path) -> Callable[[], ContextManager[sqlite3.Connection]]:
    """
    create db and table and update sensor views, if do not exists already
    and return a context managet for a DB connection
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
        CREATE TABLE IF NOT EXISTS measurements (
            time DATETIME NOT NULL,
            sensor TEXT NOT NULL,
            field TEXT NOT NULL,
            value NUMERIC NOT NULL,
            UNIQUE (time, sensor, field)
        );
        """

    with connect() as db, db, closing(db.cursor()) as cur:
        cur.executescript(create_table)

        # create a "wide table" view for every suppoorted sensor
        for sensor in Sensor:
            view_fields = ",\n".join(
                f"MAX(CASE WHEN field='{field.name}' THEN value ELSE NULL END) {field.name}"
                for field in fields(sensor.Data)
                if field.name != "time"
            )
            sensor_view = f"""
                CREATE VIEW IF NOT EXISTS {sensor.name} AS
                SELECT
                    MAX(time) time,
                    {view_fields}
                FROM
                    measurements
                WHERE
                    sensor IS '{sensor.name}'
                GROUP BY
                    time
                ORDER BY
                    time;
                """

            cur.executescript(sensor_view)

    return connect


def write_measurements(db: sqlite3.Connection, sensor: Sensor, obs: ObsData):
    """insert raw messages into the DB"""
    insert = """
        INSERT OR IGNORE INTO measurements (time, sensor, field, value)
        VALUES (?, ?, ?, ?);
        """
    values = (
        (obs.time, sensor.name, field, value)
        for field, value in asdict(obs).items()
        if field != "time"
    )
    with db, closing(db.cursor()) as cur:
        cur.executemany(insert, values)


def read_obs(db: sqlite3.Connection, sensor: Sensor) -> Generator[ObsData, None, None]:
    """read measurements from DB and return observations"""

    @dataclass
    class NewObs(sensor.Data):  # type: ignore[name-defined]
        def __post_init__(self):
            """avoid call to post-init, this was already done when the message was decoded"""
            pass

    with closing(db.cursor()) as cur:
        cur.execute(f"SELECT * FROM {sensor.name};")
        return (NewObs(*row) for row in cur.fetchall())


if __name__ == "__main__":
    from typer import run

    try:
        run(main)
    except KeyboardInterrupt:
        print("")
