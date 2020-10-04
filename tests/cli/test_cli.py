from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Callable, Generator, Union, List, Dict, Any

from pms import logger
from pms.sensor import Sensor, MessageReader
from pms.sensor.reader import RawData

import pytest
from typer.testing import CliRunner
from mypy_extensions import NamedArg

"""All captured data from /docs/sensors"""
captured_data = Path("tests/cli/captured_data/data.csv")


def read_captured_data(sensor: str) -> Generator[RawData, None, None]:
    with MessageReader(captured_data, Sensor[sensor]) as reader:
        for raw in reader(raw=True):
            yield raw


class CapturedData(Enum):
    """Captured data from /docs/sensors"""

    PMS3003 = tuple(read_captured_data("PMS3003"))
    PMSx003 = tuple(read_captured_data("PMSx003"))
    SDS01x = tuple(read_captured_data("SDS01x"))
    SDS198 = tuple(read_captured_data("SDS198"))
    MCU680 = tuple(read_captured_data("MCU680"))

    @property
    def sensor(self) -> Sensor:
        return Sensor[self.name]

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


runner = CliRunner()


@pytest.mark.parametrize("format", {"csv", "hexdump"})
def test_serial(capture, format):

    from pms.cli import main

    result = runner.invoke(main, capture.options(f"serial_{format}"))
    assert result.exit_code == 0
    assert result.stdout == capture.output(format)


def test_csv(capture):

    from pms.cli import main

    result = runner.invoke(main, capture.options("csv"))
    assert result.exit_code == 0

    csv = Path(capture.options("csv")[-1])
    assert csv.exists()
    assert csv.read_text() == capture.output("csv")
    csv.unlink()


def test_capture_decode(capture):

    from pms.cli import main

    result = runner.invoke(main, capture.options("capture"))
    assert result.exit_code == 0

    csv = Path(capture.options("capture")[-1])
    assert csv.exists()

    result = runner.invoke(main, capture.options("decode"))
    assert result.exit_code == 0
    csv.unlink()
    assert result.stdout == capture.output("csv")


@pytest.fixture()
def mock_mqtt(monkeypatch):
    """mock pms.service.mqtt.client_pub"""

    def client_pub(
        *, topic: str, host: str, port: int, username: str, password: str
    ) -> Callable[[Dict[str, Union[int, str]]], None]:
        def pub(data: Dict[str, Union[int, str]]) -> None:
            pass

        return pub

    def client_sub(
        topic: str,
        host: str,
        port: int,
        username: str,
        password: str,
        *,
        on_sensordata: Callable[[Any], None],
    ) -> None:
        pass

    monkeypatch.setattr("pms.service.mqtt.client_pub", client_pub)
    monkeypatch.setattr("pms.service.mqtt.client_sub", client_sub)


def test_mqtt(capture, mock_mqtt):

    from pms.cli import main

    result = runner.invoke(main, capture.options("mqtt"))
    assert result.exit_code == 0


@pytest.fixture()
def mock_influxdb(monkeypatch):
    """mock pms.service.influxdb.client_pub"""

    def client_pub(
        *, host: str, port: int, username: str, password: str, db_name: str
    ) -> Callable[
        [
            NamedArg(int, "time"),
            NamedArg(Dict[str, str], "tags"),
            NamedArg(Dict[str, float], "data"),
        ],
        None,
    ]:
        def pub(*, time: int, tags: Dict[str, str], data: Dict[str, float]) -> None:
            pass

        return pub

    monkeypatch.setattr("pms.service.influxdb.client_pub", client_pub)


def test_influxdb(capture, mock_influxdb):

    from pms.cli import main

    result = runner.invoke(main, capture.options("influxdb"))
    assert result.exit_code == 0
