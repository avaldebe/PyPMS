import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

os.environ["LEVEL"] = "DEBUG"
from . import CapturedData, sensor_reader


@pytest.fixture(autouse=True)
def mock_reader(monkeypatch):
    """mock pms.sensor.SensorReader"""
    monkeypatch.setattr("pms.sensor.SensorReader", sensor_reader)


runner = CliRunner()


@pytest.mark.parametrize("capture", [capture for capture in CapturedData])
def test_serial(capture: CapturedData):

    from pms.cli import main

    result = runner.invoke(main, capture.serial_options)
    assert result.exit_code == 0
    assert result.stdout == capture.output


@pytest.mark.parametrize("capture", [capture for capture in CapturedData])
def test_csv(capture: CapturedData):

    from pms.cli import main

    result = runner.invoke(main, capture.csv_options)
    assert result.exit_code == 0

    csv = Path(capture.csv_options[-1])
    assert csv.exists()
    assert csv.read_text() == capture.output
    csv.unlink()
