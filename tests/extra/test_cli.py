from dataclasses import fields
from typing import Any, Callable, Dict, Union

import pytest
from mypy_extensions import NamedArg
from typer.testing import CliRunner

from pms.extra.mqtt import Data

runner = CliRunner()


@pytest.fixture()
def mock_mqtt(monkeypatch):
    """mock pms.extra.mqtt.client_pub/client_sub"""

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

    monkeypatch.setattr("pms.extra.mqtt.client_pub", client_pub)
    monkeypatch.setattr("pms.extra.mqtt.client_sub", client_sub)


def test_mqtt(capture, mock_mqtt):

    from pms.cli import main

    result = runner.invoke(main, capture.options("mqtt"))
    assert result.exit_code == 0


@pytest.fixture()
def mock_influxdb(monkeypatch):
    """mock pms.extra.influxdb.client_pub"""

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

    monkeypatch.setattr("pms.extra.influxdb.client_pub", client_pub)


def test_influxdb(capture, mock_influxdb):

    from pms.cli import main

    result = runner.invoke(main, capture.options("influxdb"))
    assert result.exit_code == 0


@pytest.fixture()
def mock_bridge(monkeypatch, capture_data):
    """mock pms.extra.bridge.client_pub/client_sub"""

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
            tag = ",".join(f"{k},{v}" for k, v in tags.items())
            for key, val in data.items():
                print(f"{time},{tag},{key},{val}")

        return pub

    monkeypatch.setattr("pms.extra.bridge.client_pub", client_pub)

    def client_sub(
        topic: str,
        host: str,
        port: int,
        username: str,
        password: str,
        *,
        on_sensordata: Callable[[Any], None],
    ) -> None:

        for obs in capture_data.obs:
            for field in fields(obs):
                if not field.metadata:
                    continue
                topic = f"mock/test/{field.name}/{field.metadata['topic']}"
                payload = getattr(obs, field.name)
                data = Data.decode(topic, payload, time=obs.time)
                on_sensordata(data)

    monkeypatch.setattr("pms.extra.bridge.client_sub", client_sub)

    return capture_data


def test_bridge(mock_bridge):

    from pms.cli import main

    capture = mock_bridge
    result = runner.invoke(main, capture.options("bridge"))
    assert result.exit_code == 0
