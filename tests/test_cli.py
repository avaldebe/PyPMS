from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from pms.cli import APP_VERSION, main

runner = CliRunner()


@pytest.mark.parametrize("cmd", ("--version", "-V"))
def test_version(cmd: str):
    result = runner.invoke(main, cmd)
    assert result.exit_code == 0
    assert result.stdout.strip() == APP_VERSION


@pytest.mark.parametrize("format", (None, "csv", "hexdump"))
def test_serial(capture, format: str | None):
    cmd = "serial" if format is None else f"serial_{format}"
    result = runner.invoke(main, capture.options(cmd))
    assert result.exit_code == 0
    assert result.stdout == capture.output(format)


def test_csv(capture):
    result = runner.invoke(main, capture.options("csv"))
    assert result.exit_code == 0

    csv = Path(capture.options("csv")[-1])
    assert csv.is_file()
    assert csv.read_text() == capture.output("csv")
    csv.unlink()


def test_capture_decode(capture):
    result = runner.invoke(main, capture.options("capture"))
    assert result.exit_code == 0

    csv = Path(capture.options("capture")[-1])
    assert csv.exists()

    result = runner.invoke(main, capture.options("decode"))
    assert result.exit_code == 0
    csv.unlink()
    assert result.stdout == capture.output("csv")
