from __future__ import annotations

from dataclasses import fields
from typing import Callable

import pytest
from typer.testing import CliRunner

from pms.main import main

runner = CliRunner()


@pytest.fixture()
def mock_mqtt_publisher(monkeypatch: pytest.MonkeyPatch):
    """mock pms.extra.mqtt.publisher"""
    from pms.extra.mqtt import Publisher

    def publisher(*, topic: str, host: str, port: int, username: str, password: str) -> Publisher:
        def pub(data: dict[str, int | str]) -> None:
            pass

        return pub

    monkeypatch.setattr("pms.extra.mqtt.publisher", publisher)


@pytest.fixture()
def mock_mqtt_subscribe(captured_data, monkeypatch: pytest.MonkeyPatch, replay_time):
    """mock ms.extra.mqtt.subscribe"""
    from pms.extra.mqtt import Data

    def subscribe(
        topic: str,
        host: str,
        port: int,
        username: str,
        password: str,
        *,
        on_sensordata: Callable[[Data], None],
    ) -> None:
        for obs in captured_data.obs:
            for field in fields(obs):
                if not field.metadata:
                    continue
                topic = f"mock/test/{field.name}/{field.metadata['topic']}"
                payload = getattr(obs, field.name)
                data = Data.decode(topic, payload, time=obs.time)
                on_sensordata(data)

    monkeypatch.setattr("pms.extra.mqtt.subscribe", subscribe)


@pytest.fixture()
def mock_influxdb_publisher(monkeypatch: pytest.MonkeyPatch):
    """mock pms.extra.influxdb.publisher"""
    from pms.extra.influxdb import Publisher

    def publisher(*, host: str, port: int, username: str, password: str, db_name: str) -> Publisher:
        def pub(*, time: int, tags: dict[str, str], data: dict[str, float]) -> None:
            tag = ",".join(f"{k},{v}" for k, v in tags.items())
            for key, val in data.items():
                print(f"{time},{tag},{key},{val}")

        return pub

    monkeypatch.setattr("pms.extra.influxdb.publisher", publisher)


@pytest.mark.usefixtures("mock_mqtt_publisher")
def test_mqtt(capture):
    result = runner.invoke(main, capture.options("mqtt"))
    assert result.exit_code == 0


@pytest.mark.usefixtures("mock_influxdb_publisher")
def test_influxdb(capture):
    result = runner.invoke(main, capture.options("influxdb"))
    assert result.exit_code == 0


@pytest.mark.usefixtures("mock_influxdb_publisher", "mock_mqtt_subscribe")
def test_bridge(capture):
    result = runner.invoke(main, capture.options("bridge"))
    assert result.exit_code == 0
