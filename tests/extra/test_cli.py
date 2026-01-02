from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from logging import Logger

import pytest
from loguru import logger
from typer.testing import CliRunner

from pms.core.types import ObsData
from pms.extra.cli import db_measurements, mqtt_messages
from pms.main import main

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

        def enable_logger(self, logger: Logger | None = None):
            assert logger is None

        def username_pw_set(self, username: str | None, password: str | None = None):
            assert (username, password) == (None, None)

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

    mqtt = pytest.importorskip("pms.extra.mqtt")
    monkeypatch.setattr(mqtt, "Client", MockClient)


class DataPoint(NamedTuple):
    time: int
    name: str
    value: str | int | float

    def __str__(self):
        return f"{self.name} = {self.value}"

    @classmethod
    def from_obs(cls, obs_iter: Iterator[ObsData]) -> Iterator[DataPoint]:
        for obs in obs_iter:
            for name, value in db_measurements(obs):
                yield cls(obs.time, name, value)


@pytest.fixture()
def mock_influxdb_client(captured_data, monkeypatch: pytest.MonkeyPatch):
    class MockClient:
        data_point = DataPoint.from_obs(captured_data.obs)

        def __init__(
            self, host="localhost", port=8086, username="root", password="root", database=None
        ):
            assert (host, port, username, password) == ("influxdb", 8086, "root", "root")
            assert database is None

        def get_list_database(self):
            return []

        def create_database(self, dbname):
            assert dbname == "homie"
            return dbname

        def switch_database(self, database):
            pass

        def write_points(self, points, time_precision=None, database=None):
            assert time_precision == "s"
            assert database in {"homie", None}
            assert isinstance(points, list)
            for point in points:
                assert isinstance(point, dict)
                assert point.keys() == {"measurement", "tags", "time", "fields"}
                assert isinstance(point["fields"], dict)
                assert point["fields"].keys() == {"value"}
                assert DataPoint(
                    point["time"], point["measurement"], point["fields"]["value"]
                ) == next(self.data_point)

    influxdb = pytest.importorskip("pms.extra.influxdb")
    monkeypatch.setattr(influxdb, "Client", MockClient)


@pytest.fixture
def mock_mqtt_time(captured_data, monkeypatch: pytest.MonkeyPatch) -> None:
    """mock seconds_since_epoch at `pms.extra.mqtt`"""

    data_point = DataPoint.from_obs(captured_data.obs)

    def seconds_since_epoch() -> float:
        return float(next(data_point).time)

    monkeypatch.setattr("pms.extra.mqtt.seconds_since_epoch", seconds_since_epoch)


@pytest.mark.usefixtures("mock_mqtt_client")
def test_mqtt(capture):
    result = runner.invoke(main, capture.options("mqtt"))
    assert result.exit_code == 0


@pytest.mark.usefixtures("mock_influxdb_client")
def test_influxdb(capture):
    result = runner.invoke(main, capture.options("influxdb"))
    assert result.exit_code == 0


@pytest.mark.usefixtures("mock_influxdb_client", "mock_mqtt_client", "mock_mqtt_time")
def test_bridge(capture):
    result = runner.invoke(main, capture.options("bridge"))
    assert result.exit_code == 0
