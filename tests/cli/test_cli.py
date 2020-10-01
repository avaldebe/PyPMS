import os
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, Union, List, Dict, Any

import pytest
from typer.testing import CliRunner
from mypy_extensions import NamedArg

os.environ["LEVEL"] = "DEBUG"

"""All captured data from /docs/sensors"""
captured_data = Path("tests/cli/captured_data/data.csv")


@pytest.fixture(autouse=True)
def mock_reader(monkeypatch):
    """mock pms.sensor.SensorReader"""
    from pms.sensor import Sensor
    from pms.sensor.cli import MesageReader

    class MockReader(MesageReader):
        def __init__(
            self, sensor: str, port: str, interval: int, samples: Optional[int] = None
        ) -> None:
            super().__init__(captured_data, Sensor[sensor], samples)

    monkeypatch.setattr("pms.sensor.SensorReader", MockReader)


class CapturedData(Enum):
    """Captured data from /docs/sensors"""

    PMS3003 = "PMS3003"
    PMSx003 = "PMSx003"
    SDS01x = "SDS01x"
    SDS198 = "SDS198"
    MCU680 = "MCU680"

    @property
    def samples(self) -> int:
        return sum(self.name in line for line in self.csv.split("\n"))

    @property
    def interval(self) -> int:
        return 10

    @property
    def options(self) -> Dict[str, List[str]]:
        capture = f"-m {self.name} -s {self.samples} -i {self.interval}"
        return dict(
            serial=f"{capture} serial -f csv".split(),
            csv=f"{capture} csv --overwrite {self.name}_test.csv".split(),
            capture=f"{capture} csv --overwrite  --capture {self.name}_pypms.csv".split(),
            decode=f"{capture} serial -f csv --decode {self.name}_pypms.csv".split(),
            mqtt=f"{capture} mqtt".split(),
            influxdb=f"{capture} influxdb".split(),
        )

    @property
    def csv(self) -> str:
        csv = captured_data.parent / f"{self.name}.csv"
        return csv.read_text()


@pytest.fixture(params=[capture for capture in CapturedData])
def capture(request) -> CapturedData:
    return request.param


runner = CliRunner()


def test_serial(capture):

    from pms.cli import main

    result = runner.invoke(main, capture.options["serial"])
    assert result.exit_code == 0
    assert result.stdout == capture.csv


def test_csv(capture):

    from pms.cli import main

    result = runner.invoke(main, capture.options["csv"])
    assert result.exit_code == 0

    csv = Path(capture.options["csv"][-1])
    assert csv.exists()
    assert csv.read_text() == capture.csv
    csv.unlink()


def test_capture_decode(capture):

    from pms.cli import main

    result = runner.invoke(main, capture.options["capture"])
    assert result.exit_code == 0

    csv = Path(capture.options["capture"][-1])
    assert csv.exists()

    result = runner.invoke(main, capture.options["decode"])
    assert result.exit_code == 0
    csv.unlink()

    # freezegun.timestamps don't match https://github.com/spulec/freezegun/issues/346
    # compare only the end of the lines
    for stdout, line in zip(result.stdout.split("\n"), capture.csv.split("\n")):
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

    result = runner.invoke(main, capture.options["mqtt"])
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

    result = runner.invoke(main, capture.options["influxdb"])
    assert result.exit_code == 0
