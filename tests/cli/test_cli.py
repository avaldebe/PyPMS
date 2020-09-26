import os
from pathlib import Path
from typing import Callable, Dict, Union, Any

import pytest
from typer.testing import CliRunner
from mypy_extensions import NamedArg

os.environ["LEVEL"] = "DEBUG"

from . import CapturedData, MockReader


@pytest.fixture(autouse=True)
def mock_reader(monkeypatch):
    """mock pms.sensor.SensorReader"""
    monkeypatch.setattr("pms.sensor.SensorReader", MockReader)


runner = CliRunner()


@pytest.mark.parametrize("capture", [capture for capture in CapturedData])
def test_serial(capture: CapturedData):

    from pms.cli import main

    result = runner.invoke(main, capture.options["serial"])
    assert result.exit_code == 0
    assert result.stdout == capture.csv


@pytest.mark.parametrize("capture", [capture for capture in CapturedData])
def test_csv(capture: CapturedData):

    from pms.cli import main

    result = runner.invoke(main, capture.options["csv"])
    assert result.exit_code == 0

    csv = Path(capture.options["csv"][-1])
    assert csv.exists()
    assert csv.read_text() == capture.csv
    csv.unlink()


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


@pytest.mark.parametrize("capture", [capture for capture in CapturedData])
def test_mqtt(capture: CapturedData, mock_mqtt):

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


@pytest.mark.parametrize("capture", [capture for capture in CapturedData])
def test_influxdb(capture: CapturedData, mock_influxdb):

    from pms.cli import main

    result = runner.invoke(main, capture.options["influxdb"])
    assert result.exit_code == 0
