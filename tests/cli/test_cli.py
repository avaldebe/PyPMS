from enum import Enum
from pathlib import Path
from typing import Callable, Union, List, Dict, Any

import pytest
from typer.testing import CliRunner
from mypy_extensions import NamedArg

"""All captured data from /docs/sensors"""
captured_data = Path("tests/cli/captured_data/data.csv")


class CapturedData(Enum):
    """Captured data from /docs/sensors"""

    PMS3003 = "PMS3003"
    PMSx003 = "PMSx003"
    SDS01x = "SDS01x"
    SDS198 = "SDS198"
    MCU680 = "MCU680"

    @property
    def samples(self) -> int:
        text = captured_data.read_text().split("\n")
        return sum(self.name in line for line in text)

    @property
    def interval(self) -> int:
        return 10

    def options(self, command: str) -> List[str]:
        samples = self.samples
        if "csv" in command or command == "mqtt":
            samples -= 1
        capture = f"-m {self.name} -n {samples} -i {self.interval}"
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
    from pms import logger
    from pms.sensor import Sensor, MessageReader

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

    sensor = Sensor[request.param.name]
    with MessageReader(captured_data, sensor) as reader:
        data = b"".join(message for message in reader(raw=True))

    def mock_reader__cmd(self, command: str) -> bytes:
        """bypass serial.write/read"""
        nonlocal data, sensor
        size = sensor.command(command).answer_length
        logger.debug(f"mock read({size}), {len(data)} bytes left")
        if command == "passive_read":
            answer, data = data[:size], data[size:]
        else:
            answer = b"." * size
        return answer

    monkeypatch.setattr("pms.sensor.reader.SensorReader._cmd", mock_reader__cmd)

    def mock_sensor_check(self, buffer: bytes, command: str) -> bool:
        """don't check if message matches sensor"""
        return True

    monkeypatch.setattr("pms.sensor.reader.Sensor.check", mock_sensor_check)

    def mock_time_sleep(secs: float):
        """don't wait for next sample"""
        pass

    monkeypatch.setattr("time.sleep", mock_time_sleep)

    return request.param


runner = CliRunner()


@pytest.mark.parametrize("format", {"csv", "hexdump"})
def test_serial(capture, format):

    from pms.cli import main

    result = runner.invoke(main, capture.options(f"serial_{format}"))
    assert result.exit_code == 0
    # freezegun.timestamps don't match https://github.com/spulec/freezegun/issues/346
    # compare only the end of the lines
    if format == "csv":
        for stdout, line in zip(result.stdout.split("\n"), capture.output("csv").split("\n")):
            assert stdout[10:] == line[10:]
    else:
        assert result.stdout == capture.output(format)


def test_csv(capture):

    from pms.cli import main

    result = runner.invoke(main, capture.options("csv"))
    assert result.exit_code == 0

    csv = Path(capture.options("csv")[-1])
    assert csv.exists()
    # assert csv.read_text() == capture.output("csv")
    # freezegun.timestamps don't match https://github.com/spulec/freezegun/issues/346
    # compare only the end of the lines
    for csvout, line in zip(csv.read_text().split("\n"), capture.output("csv").split("\n")):
        assert csvout[10:] == line[10:]
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

    # assert result.stdout == capture.output("csv")
    # freezegun.timestamps don't match https://github.com/spulec/freezegun/issues/346
    # compare only the end of the lines
    for stdout, line in zip(result.stdout.split("\n"), capture.output("csv").split("\n")):
        assert stdout[10:] == line[10:]


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
