import sys
from contextlib import closing, contextmanager
from csv import DictReader
from enum import Enum
from pathlib import Path
from sqlite3 import connect
from typing import Iterator, List

import pytest

from pms import logger
from pms.core import Sensor
from pms.core.reader import RawData
from pms.core.types import ObsData

captured_data = Path("tests/captured_data/data.csv")


@contextmanager
def captured_data_reader(db_str: str = ":memory:", *, data: Path = None):
    db = connect(db_str)
    with db, closing(db.cursor()) as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                time DATETIME NOT NULL, 
                sensor TEXT NOT NULL, 
                message BLOB NOT NULL,
                UNIQUE (time, sensor)
            )
            """
        )

    if data is not None and data.exists():
        db.create_function("bytes", 1, bytes.fromhex)
        insert = "INSERT OR IGNORE INTO messages (time, sensor, message) VALUES (:time, :sensor, bytes(:hex))"
        with db, closing(db.cursor()) as cur, data.open() as csv:
            cur.executemany(insert, DictReader(csv))

    def reader(sensor: str) -> Iterator[RawData]:
        select = f"SELECT time, message FROM messages WHERE sensor IS '{sensor}'"
        with closing(db.cursor()) as cur:
            cur.execute(select)
            return (RawData(*row) for row in cur.fetchall())

    try:
        yield reader
    finally:
        db.close()


class CapturedData(Enum):
    """Captured data from tests/captured_data"""

    _ignore_ = "name capt CapturedData"

    with captured_data_reader(data=captured_data) as reader:
        CapturedData = vars()
        for name in [s.name for s in Sensor]:
            capt = tuple(reader(name))
            if capt:
                CapturedData[name] = capt

    def __str__(self) -> str:
        return self.name

    @property
    def sensor(self) -> Sensor:
        return Sensor[self.name]

    @property
    def data(self) -> Iterator[bytes]:
        return (msg.data for msg in self.value)

    @property
    def time(self) -> Iterator[int]:
        return (msg.time for msg in self.value)

    @property
    def obs(self) -> Iterator[ObsData]:
        sensor = self.sensor
        return (sensor.decode(msg.data, time=msg.time) for msg in self.value)

    def options(self, command: str) -> List[str]:
        samples = len(self.value)
        if command == "mqtt":
            samples -= 1
        capture = f"-m {self.name} -n {samples} -i 0"
        cmd = dict(
            serial_csv=f"serial -f csv",
            serial_hexdump=f"serial -f hexdump",
            csv=f"csv --overwrite {self.name}_test.csv",
            capture=f"csv --overwrite  --capture {self}_pypms.csv",
            decode=f"serial -f csv --decode {self}_pypms.csv",
        ).get(command, command)
        return f"{capture} --debug {cmd}".split()

    def output(self, ending: str) -> str:
        path = captured_data.parent / f"{self}.{ending}"
        return path.read_text()


@pytest.fixture(params=list(CapturedData), ids=str)
def capture_data(request) -> CapturedData:
    """captured data from real sensors"""
    return request.param


@pytest.fixture()
def capture(monkeypatch, capture_data) -> CapturedData:
    """mock pms.core.reader.Serial and some pms.core.reader.SensorReader internals"""

    class MockSerial:
        port = None
        baudrate = None
        timeout = None
        is_open = False

        def open(self):
            self.is_open = True

        def close(self):
            self.is_open = False

        def reset_input_buffer(self):
            pass

    monkeypatch.setattr("pms.core.reader.Serial", MockSerial)

    sensor = capture_data.sensor
    data = capture_data.data

    def mock_reader__cmd(self, command: str) -> bytes:
        """bypass serial.write/read"""
        logger.debug(f"mock write/read: {command}")
        # nonlocal data
        if command == "passive_read":
            return next(data)
        if command in ["wake", "passive_mode"]:
            return b"." * sensor.command(command).answer_length

        return b""

    monkeypatch.setattr("pms.core.reader.SensorReader._cmd", mock_reader__cmd)

    def mock_reader__pre_heat(self):
        pass

    monkeypatch.setattr("pms.core.reader.SensorReader._pre_heat", mock_reader__pre_heat)

    def mock_sensor_check(self, buffer: bytes, command: str) -> bool:
        """don't check if message matches sensor"""
        return True

    monkeypatch.setattr("pms.core.reader.Sensor.check", mock_sensor_check)

    time = capture_data.time

    def mock_sensor_now(self) -> int:
        """mock pms.core.Sensor.now"""
        nonlocal time
        return next(time)

    monkeypatch.setattr("pms.core.reader.Sensor.now", mock_sensor_now)

    return capture_data
