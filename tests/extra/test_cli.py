from typing import Any, Callable, Dict, Union

import pytest
from mypy_extensions import NamedArg
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture()
def mock_mqtt(monkeypatch):
    """mock pypms.extra.mqtt.client_pub"""

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

    monkeypatch.setattr("pypms.extra.mqtt.client_pub", client_pub)
    monkeypatch.setattr("pypms.extra.mqtt.client_sub", client_sub)


def test_mqtt(capture, mock_mqtt):

    from pms.cli import main

    result = runner.invoke(main, capture.options("mqtt"))
    assert result.exit_code == 0


@pytest.fixture()
def mock_influxdb(monkeypatch):
    """mock pypms.extra.influxdb.client_pub"""

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

    monkeypatch.setattr("pypms.extra.influxdb.client_pub", client_pub)


def test_influxdb(capture, mock_influxdb):

    from pms.cli import main

    result = runner.invoke(main, capture.options("influxdb"))
    assert result.exit_code == 0
