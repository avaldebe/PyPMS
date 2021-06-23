from enum import Enum
from pathlib import Path
from typing import Generator, List

import pytest

from pms import logger
from pms.sensor import MessageReader, Sensor
from pms.sensor.reader import RawData

logger.setLevel("DEBUG")
captured_data = Path("tests/captured_data/data.csv")


def read_captured_data(sensor: str) -> Generator[RawData, None, None]:
    with MessageReader(captured_data, Sensor[sensor]) as reader:  # type: ignore
        for raw in reader(raw=True):
            yield raw


class CapturedData(Enum):
    """Captured data from /docs/sensors"""

    PMS3003 = tuple(read_captured_data("PMS3003"))
    PMSx003 = tuple(read_captured_data("PMSx003"))
    PMS5003T = tuple(read_captured_data("PMS5003T"))
    SDS01x = tuple(read_captured_data("SDS01x"))
    SDS198 = tuple(read_captured_data("SDS198"))
    MCU680 = tuple(read_captured_data("MCU680"))

    @property
    def sensor(self) -> Sensor:
        return Sensor[self.name]  # type: ignore

    @property
    def data(self) -> Generator[bytes, None, None]:
        return (msg.data for msg in self.value)

    @property
    def time(self) -> Generator[int, None, None]:
        return (msg.time for msg in self.value)

    def options(self, command: str) -> List[str]:
        samples = len(self.value)
        if "csv" in command or command == "mqtt":
            samples -= 1
        capture = f"-m {self.name} -n {samples} -i 0"
        cmd = dict(
            serial_csv=f"serial -f csv",
            serial_hexdump=f"serial -f hexdump",
            csv=f"csv --overwrite {self.name}_test.csv",
            capture=f"csv --overwrite  --capture {self.name}_pypms.csv",
            decode=f"serial -f csv --decode {self.name}_pypms.csv",
            mqtt=f"mqtt",
            influxdb=f"influxdb",
        )[command]
        return f"{capture} --debug {cmd}".split()

    def output(self, ending: str) -> str:
        path = captured_data.parent / f"{self.name}.{ending}"
        return path.read_text()


@pytest.fixture(params=[capture for capture in CapturedData])
def capture(monkeypatch, request) -> CapturedData:
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

    monkeypatch.setattr("pms.sensor.reader.Serial", MockSerial)

    data = request.param.data

    def mock_reader__cmd(self, command: str) -> bytes:
        """bypass serial.write/read"""
        logger.debug(f"mock write/read: {command}")
        nonlocal data
        return next(data) if command == "passive_read" else b""

    monkeypatch.setattr("pms.sensor.reader.SensorReader._cmd", mock_reader__cmd)

    def mock_sensor_check(self, buffer: bytes, command: str) -> bool:
        """don't check if message matches sensor"""
        return True

    monkeypatch.setattr("pms.sensor.reader.Sensor.check", mock_sensor_check)

    time = request.param.time

    def mock_sensor_now(self) -> int:
        """mock pms.sensor.Sensor.now"""
        nonlocal time
        return next(time)

    monkeypatch.setattr("pms.sensor.reader.Sensor.now", mock_sensor_now)

    return request.param