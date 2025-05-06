from __future__ import annotations

from collections.abc import Iterator
from typing import NamedTuple

import pytest
from loguru import logger
from typer.testing import CliRunner

from pms.extra.cli import db_measurements, mqtt_messages
from pms.main import main
from pms.sensors.base import ObsData

runner = CliRunner()


class Message(NamedTuple):
    topic: str
    payload: str | int | float

    def __str__(self):
        return f"{self.topic} = {self.payload}"

    @classmethod
    def from_obs(cls, obs_iter: Iterator[ObsData]) -> Iterator[Message]:
        for obs in obs_iter:
            for topic, payload in mqtt_messages(obs):
                yield cls(f"homie/test/{topic}", payload)


@pytest.fixture()
def mock_mqtt_client(captured_data, monkeypatch: pytest.MonkeyPatch):
    class MockClient:
        _message = Message.from_obs(captured_data.obs)
        on_message = None
        on_connect = None

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
                assert Message(topic, payload) == next(self._message)

        def loop_start(self):
            logger.debug("loop_start")
            assert self.on_connect is not None
            assert self.on_message is None

        def loop_forever(self, timeout=1, retry_first_connection=False):
            logger.debug("loop_forever")
            assert self.on_connect is not None
            assert self.on_message is not None
            for msg in self._message:
                self.on_message(self, None, msg)

    monkeypatch.setattr("pms.extra.mqtt.Client", MockClient)


class Measurement(NamedTuple):
    field: str
    value: str | int | float

    def __str__(self):
        return f"{self.field} = {self.value}"

    @classmethod
    def from_obs(cls, obs_iter: Iterator[ObsData]) -> Iterator[Measurement]:
        for obs in obs_iter:
            for field, value in db_measurements(obs):
                yield cls(field, value)


@pytest.fixture()
def mock_influxdb_publisher(captured_data, monkeypatch: pytest.MonkeyPatch):
    """mock pms.extra.influxdb.publisher"""
    from pms.extra.influxdb import Publisher

    def publisher(*, host: str, port: int, username: str, password: str, db_name: str) -> Publisher:
        measurement = Measurement.from_obs(captured_data.obs)

        def pub(*, time: int, tags: dict[str, str], data: dict[str, float]) -> None:
            assert tags == {"location": "test"}
            for field, value in data.items():
                assert Measurement(field, value) == next(measurement)

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


@pytest.mark.usefixtures("mock_influxdb_publisher", "mock_mqtt_client")
def test_bridge(capture):
    result = runner.invoke(main, capture.options("bridge"))
    assert result.exit_code == 0
