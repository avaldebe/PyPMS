from __future__ import annotations

from collections.abc import Iterator
from dataclasses import fields
from typing import Callable

import pytest
from loguru import logger
from typer.testing import CliRunner

from pms.main import main

runner = CliRunner()


@pytest.fixture()
def mock_mqtt_client(captured_data, monkeypatch: pytest.MonkeyPatch):
    from pms.extra.mqtt import Data

    def mqtt_messages() -> Iterator[Data]:
        for obs in captured_data.obs:
            for field in fields(obs):
                if not field.metadata:
                    continue
                yield Data(obs.time, "test", field.name, getattr(obs, field.name))

    class MockClient:
        _message = mqtt_messages()

        def __init__(self, *, client_id: str):
            assert client_id in {"homie/test", "homie/+/+/+"}

        def enable_logger(self, logger):  # noqa: F811
            pass

        def username_pw_set(self, username: str | None, password: str | None = None):
            assert username is None
            assert password is None

        def will_set(self, topic, payload=None, qos=0, retain=False, properties=None):
            assert topic.endswith("$online")
            assert payload == "false"
            assert qos == 1
            assert retain is True

        def connect(self, host, port=1883):
            assert host == "test.mosquitto.org"
            assert port == 1883  # MQTT, unencrypted, unauthenticated

        def publish(self, topic, payload=None, qos=0, retain=False, properties=None):
            logger.debug(f"{topic} = {payload}")
            assert topic.startswith("homie/test/")
            assert isinstance(payload, (str, float, int))
            assert qos == 1
            assert retain is True
            if isinstance(payload, (float, int)):
                logger.debug(msg := next(self._message))
                assert Data.decode(topic, payload, time=msg.time) == msg

        def _handle_on_message(self, message):
            logger.debug("_handle_on_message")
            assert self.on_message is not None

        def loop_start(self):
            logger.debug("loop_start")

        def loop_forever(self, timeout=1, retry_first_connection=False):
            logger.debug("loop_forever")

    monkeypatch.setattr("pms.extra.mqtt.Client", MockClient)


@pytest.fixture()
def mock_mqtt_subscribe(captured_data, monkeypatch: pytest.MonkeyPatch):
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
                logger.debug(f"{time},{tag},{key},{val}")

        return pub

    monkeypatch.setattr("pms.extra.influxdb.publisher", publisher)


@pytest.mark.usefixtures("mock_mqtt_client")
def test_mqtt(capture):
    result = runner.invoke(main, capture.options("mqtt", debug=True))
    assert result.exit_code == 0


@pytest.mark.usefixtures("mock_influxdb_publisher")
def test_influxdb(capture):
    result = runner.invoke(main, capture.options("influxdb"))
    assert result.exit_code == 0


@pytest.mark.usefixtures("mock_influxdb_publisher", "mock_mqtt_subscribe")
def test_bridge(capture):
    result = runner.invoke(main, capture.options("bridge"))
    assert result.exit_code == 0
