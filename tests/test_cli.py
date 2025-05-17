from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from loguru import logger
from typer.testing import CliRunner

from pms import __version__
from pms.main import main

runner = CliRunner()


@pytest.fixture
def caplog(caplog: pytest.LogCaptureFixture):
    logger.disable("tests")
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)
    logger.enable("tests")


@pytest.mark.parametrize("cmd", ("--version", "-V"))
def test_version(cmd: str, caplog: pytest.LogCaptureFixture):
    result = runner.invoke(main, cmd)
    assert result.exit_code == 0
    assert result.output.strip() == f"PyPMS v{__version__}"

    assert not caplog.text


def test_info(capture, caplog: pytest.LogCaptureFixture):
    result = runner.invoke(main, capture.options("info"))
    assert result.exit_code == 0
    assert dedent(result.output).strip() == capture.output("info").strip()

    logs = caplog.text.splitlines()
    assert logs[0].endswith(f"PyPMS v{__version__}")
    assert logs[1].endswith(f"{capture} ... info")


@pytest.mark.parametrize("format", (None, "csv", "hexdump"))
def test_serial(capture, format: str | None, caplog: pytest.LogCaptureFixture):
    cmd = "serial" if format is None else f"serial_{format}"
    result = runner.invoke(main, capture.options(cmd))
    assert result.exit_code == 0
    assert result.output == capture.output(format)

    logs = caplog.text.splitlines()
    assert logs[0].endswith(f"PyPMS v{__version__}")
    assert logs[1].endswith(f"{capture} ... serial")


def test_csv(capture, caplog: pytest.LogCaptureFixture):
    result = runner.invoke(main, capture.options("csv"))
    assert result.exit_code == 0

    csv = Path(capture.options("csv")[-1])
    assert csv.is_file()
    assert csv.read_text() == capture.output("csv")
    csv.unlink()

    logs = caplog.text.splitlines()
    assert logs[0].endswith(f"PyPMS v{__version__}")
    assert logs[1].endswith(f"{capture} ... csv")


def test_capture_decode(capture, caplog: pytest.LogCaptureFixture):
    result = runner.invoke(main, capture.options("capture"))
    assert result.exit_code == 0
    csv = Path(capture.options("capture")[-1])
    assert csv.exists()

    logs = caplog.text.splitlines()
    assert logs[0].endswith(f"PyPMS v{__version__}")
    assert logs[1].endswith(f"{capture} ... csv")
    caplog.clear()

    result = runner.invoke(main, capture.options("decode"))
    assert result.exit_code == 0
    csv.unlink()
    assert result.output == capture.output("csv")

    logs = caplog.text.splitlines()
    assert logs[0].endswith(f"PyPMS v{__version__}")
    assert logs[1].endswith(f"{capture} ... serial")
