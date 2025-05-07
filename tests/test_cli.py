from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from logot import Logot, logged
from typer.testing import CliRunner

from pms import __version__
from pms.main import main

runner = CliRunner()


@pytest.mark.parametrize("cmd", ("--version", "-V"))
def test_version(cmd: str, logot: Logot):
    result = runner.invoke(main, cmd)
    assert result.exit_code == 0
    assert result.stdout.strip() == f"PyPMS v{__version__}"
    logot.assert_not_logged(logged.debug(f"PyPMS v{__version__}"))


def test_info(capture, logot: Logot):
    result = runner.invoke(main, capture.options("info"))
    assert result.exit_code == 0
    assert dedent(result.stdout).strip() == capture.output("info").strip()
    logot.assert_logged(logged.debug(f"PyPMS v{__version__}"))


@pytest.mark.parametrize("format", (None, "csv", "hexdump"))
def test_serial(capture, format: str | None, logot: Logot):
    cmd = "serial" if format is None else f"serial_{format}"
    result = runner.invoke(main, capture.options(cmd))
    assert result.exit_code == 0
    assert result.stdout == capture.output(format)

    for msg in capture.debug_messages("serial"):
        logot.assert_logged(logged.debug(msg))


def test_csv(capture, logot: Logot):
    result = runner.invoke(main, capture.options("csv"))
    assert result.exit_code == 0

    csv = Path(capture.options("csv")[-1])
    assert csv.is_file()
    assert csv.read_text() == capture.output("csv")
    csv.unlink()

    for msg in capture.debug_messages("csv"):
        logot.assert_logged(logged.debug(msg))


def test_capture_decode(capture, logot: Logot):
    result = runner.invoke(main, capture.options("capture"))
    assert result.exit_code == 0
    csv = Path(capture.options("capture")[-1])
    assert csv.exists()

    for msg in capture.debug_messages("capture"):
        logot.assert_logged(logged.debug(msg))

    result = runner.invoke(main, capture.options("decode"))
    assert result.exit_code == 0
    csv.unlink()
    assert result.stdout == capture.output("csv")

    for msg in capture.debug_messages("decode"):
        logot.assert_logged(logged.debug(msg))
