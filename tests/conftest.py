from __future__ import annotations

from collections.abc import Iterator
from contextlib import closing, contextmanager
from csv import DictReader
from datetime import datetime, tzinfo
from enum import Enum
from pathlib import Path
from sqlite3 import connect
from zoneinfo import ZoneInfo

import pytest
from loguru import logger

from pms import __version__
from pms.core import Sensor
from pms.core.reader import RawData
from pms.core.types import ObsData

CAPTURED_DATA = Path("tests/captured_data/data.csv")


@contextmanager
def captured_data_reader(db_str: str = ":memory:", *, data: Path | None = None):
    db = connect(db_str)
    with db, closing(db.cursor()) as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            time DATETIME NOT NULL,
            sensor TEXT NOT NULL,
            message BLOB NOT NULL,
            UNIQUE (time, sensor)
        )
        """)

    if data is not None and data.exists():
        db.create_function("bytes", 1, bytes.fromhex)
        with db, closing(db.cursor()) as cur, data.open() as csv:
            cur.executemany(
                """
                INSERT OR IGNORE INTO messages
                    (time, sensor, message)
                VALUES
                    (:time, :sensor, bytes(:hex))
                """,
                DictReader(csv),
            )

    def reader(sensor: str) -> Iterator[RawData]:
        with closing(db.cursor()) as cur:
            cur.execute(
                "SELECT time, message FROM messages WHERE sensor IS ?",
                (sensor,),
            )
            return (RawData(*row) for row in cur.fetchall())

    try:
        yield reader
    finally:
        db.close()


class CapturedData(Enum):
    """Captured data from tests/captured_data"""

    _ignore_ = "name capt CapturedData reader"

    with captured_data_reader(data=CAPTURED_DATA) as reader:
        CapturedData = vars()
        for name in (s.name for s in Sensor):
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
    def tzinfo(self) -> tzinfo:
        return ZoneInfo("Europe/Oslo")

    @property
    def obs(self) -> Iterator[ObsData]:
        sensor = self.sensor
        return (sensor.decode(msg.data, time=msg.time) for msg in self.value)

    @property
    def msg_hex(self) -> Iterator[str]:
        for message in self.value:
            if self.name == "SPS30":
                yield (
                    message.hex.replace("7d5e", "7e")
                    .replace("7d5d", "7d")
                    .replace("7d31", "11")
                    .replace("7d33", "13")
                )
            else:
                yield message.hex

    def samples(self, command: str) -> int:
        return len(self.value) - (command == "mqtt")

    def options(self, command: str) -> list[str]:
        capture = f"-m {self.name} -n {self.samples(command)} -i 0"
        cmd = dict(
            serial_csv="serial -f csv",
            serial_hexdump="serial -f hexdump",
            csv=f"csv --overwrite {self.name}_test.csv",
            capture=f"csv --overwrite --capture {self}_pypms.csv",
            decode=f"serial -f csv --decode {self}_pypms.csv",
        ).get(command, command)
        return f"--debug {capture} {cmd}".split()

    def output(self, ending: str | None) -> str:
        if ending is None:
            ending = "txt"
        path = CAPTURED_DATA.with_name(f"{self}.{ending}")
        return path.read_text()

    def debug_messages(self, command: str) -> Iterator[str]:
        yield f"PyPMS v{__version__}"
        if command == "decode":
            yield f"open {self}_pypms.csv"
            yield f"close {self}_pypms.csv"
            return

        yield f"capture {self.samples(command)} {self.name} obs from /dev/ttyUSB0 every ? secs"
        yield "open /dev/ttyUSB0"
        yield f"wake {self.name}"
        for hex in self.msg_hex:
            yield f"message hex: {hex}"
        yield f"sleep {self.name}"
        yield "close /dev/ttyUSB0"


@pytest.fixture(params=CapturedData, ids=str)
def capture_data(request: pytest.FixtureRequest) -> CapturedData:
    """captured data from real sensors"""
    return request.param


@pytest.fixture()
def capture(monkeypatch: pytest.MonkeyPatch, capture_data: CapturedData) -> CapturedData:
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

    captured_data = capture_data.data

    def mock_reader__cmd(self, command: str) -> bytes:
        """bypass serial.write/read"""
        logger.debug(f"mock write/read: {command}")
        # nonlocal data
        if command == "passive_read":
            return next(captured_data)
        if command in {"wake", "passive_mode"}:
            return b"." * self.sensor.command(command).answer_length

        return b""

    def mock_reader__pre_heat(self) -> int:
        return 0

    def mock_sensor_check(self, buffer: bytes, command: str) -> bool:
        """don't check if message matches sensor"""
        return True

    class mock_datetime(datetime):
        captured_time = capture_data.time

        @classmethod
        def fromtimestamp(cls, t, tz=capture_data.tzinfo):
            assert tz == capture_data.tzinfo
            return datetime.fromtimestamp(t, tz)

        @classmethod
        def now(cls, tz=capture_data.tzinfo):
            return cls.fromtimestamp(next(cls.captured_time), tz)

    monkeypatch.setattr("pms.core.reader.Serial", MockSerial)
    monkeypatch.setattr("pms.core.reader.SensorReader._cmd", mock_reader__cmd)
    monkeypatch.setattr("pms.core.reader.SensorReader._pre_heat", mock_reader__pre_heat)
    monkeypatch.setattr("pms.core.reader.Sensor.check", mock_sensor_check)
    monkeypatch.setattr("pms.core.sensor.datetime", mock_datetime)
    monkeypatch.setattr("pms.sensors.base.datetime", mock_datetime)

    return capture_data
