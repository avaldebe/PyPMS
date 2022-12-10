from pathlib import Path

import pytest
from typer.testing import CliRunner

runner = CliRunner()


@pytest.mark.parametrize("format", {"csv", "hexdump"})
def test_serial(capture, format):

    from pms.cli import app

    result = runner.invoke(app, capture.options(f"serial_{format}"))
    assert result.exit_code == 0
    assert result.stdout == capture.output(format)


def test_csv(capture):

    from pms.cli import app

    result = runner.invoke(app, capture.options("csv"))
    assert result.exit_code == 0

    csv = Path(capture.options("csv")[-1])
    assert csv.exists()
    assert csv.read_text() == capture.output("csv")
    csv.unlink()


def test_capture_decode(capture):

    from pms.cli import app

    result = runner.invoke(app, capture.options("capture"))
    assert result.exit_code == 0

    csv = Path(capture.options("capture")[-1])
    assert csv.exists()

    result = runner.invoke(app, capture.options("decode"))
    assert result.exit_code == 0
    csv.unlink()
    assert result.stdout == capture.output("csv")
