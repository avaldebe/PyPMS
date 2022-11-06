import pytest

from pms.core import reader
from pms.core.sensor import Sensor
from tests.conftest import captured_data


class MockReader(reader.Reader):
    def __init__(self, raise_on_enter=False):
        self.raise_on_enter = raise_on_enter

    def __call__(self):
        raise NotImplemented

    def __enter__(self):
        if self.raise_on_enter:
            raise reader.UnableToRead()
        self.entered = True

    def __exit__(self, *_args):
        self.exited = True


@pytest.fixture
def mock_sleep(monkeypatch):
    def sleep(seconds):
        sleep.slept_for += seconds

    sleep.slept_for = 0

    monkeypatch.setattr(
        reader.time,
        "sleep",
        sleep,
    )

    return sleep


@pytest.fixture
def mock_sensor(mock_serial):
    mock_serial.stub(
        name="wake",
        receive_bytes=b"BM\xe4\x00\x01\x01t",
        send_bytes=(
            b"BM\x00\x1c"  # expected header
            + b".........................."  # payload (to total 32 bytes)
            + b"\x05W"  # checksum = sum(header) + sum(payload)
        ),
    )

    mock_serial.stub(
        name="passive_mode",
        receive_bytes=b"BM\xe1\x00\x00\x01p",
        send_bytes=(
            b"BM\x00\x04"  # expected header
            + b".."  # payload (to total 8 bytes)
            + b"\x00\xef"  # checksum
        ),
    )

    mock_serial.stub(
        name="passive_read",
        receive_bytes=b"BM\xe2\x00\x00\x01q",
        send_bytes=(
            b"BM\x00\x1c"  # expected header
            + b".........................."  # payload (to total 32 bytes)
            + b"\x05W"  # checksum
        ),
    )

    mock_serial.stub(
        name="sleep",
        receive_bytes=b"BM\xe4\x00\x00\x01s",
        send_bytes=(
            b"BM\x00\x04"  # expected header
            + b".."  # payload (to total 8 bytes)
            + b"\x00\xef"  # checksum
        ),
    )

    return mock_serial


def test_sensor_reader(mock_sensor, monkeypatch):
    sensor_reader = reader.SensorReader(
        port=mock_sensor.port,
        samples=0,  # exit immediately
        sensor="PMSx003",  # match with stubs
        timeout=0.01,  # low to avoid hanging on failure
    )

    # https://github.com/pyserial/pyserial/issues/625
    monkeypatch.setattr(
        sensor_reader.serial,
        "flush",
        lambda: None,
    )

    with sensor_reader as r:
        obs = list(r())

    # check warm up happened
    assert mock_sensor.stubs["wake"].called
    assert mock_sensor.stubs["passive_mode"].called

    # check data was read
    assert len(obs) == 1
    assert obs[0].pm10 == 11822

    # check sleep happened
    assert mock_sensor.stubs["sleep"].called


def test_sensor_reader_sleep(mock_sensor, monkeypatch, mock_sleep):
    sensor_reader = reader.SensorReader(
        port=mock_sensor.port,
        samples=2,  # try to read twice
        interval=5,  # sleep between samples
        sensor="PMSx003",  # match with stubs
        timeout=0.01,  # low to avoid hanging on failure
    )

    # https://github.com/pyserial/pyserial/issues/625
    monkeypatch.setattr(
        sensor_reader.serial,
        "flush",
        lambda: None,
    )

    with sensor_reader as r:
        obs = list(r())

    # check we read twice
    assert len(obs) == 2

    # check we slept between reads
    assert 0 < mock_sleep.slept_for < 5


def test_sensor_reader_closed(mock_sensor, monkeypatch):
    sensor_reader = reader.SensorReader(
        port=mock_sensor.port,
        sensor="PMSx003",  # match with stubs
        timeout=0.01,  # low to avoid hanging on failure
    )

    # https://github.com/pyserial/pyserial/issues/625
    monkeypatch.setattr(
        sensor_reader.serial,
        "flush",
        lambda: None,
    )

    obs = list(sensor_reader())
    assert len(obs) == 0


def test_sensor_reader_preheat(mock_sensor, monkeypatch, mock_sleep):
    sensor_reader = reader.SensorReader(
        port=mock_sensor.port,
        sensor="PMSx003",  # match with stubs
        timeout=0.01,  # low to avoid hanging on failure
    )

    # https://github.com/pyserial/pyserial/issues/625
    monkeypatch.setattr(
        sensor_reader.serial,
        "flush",
        lambda: None,
    )

    # override pre heat duration
    sensor_reader.pre_heat = 5

    with sensor_reader as r:
        pass

    # check we slept between reads
    assert mock_sleep.slept_for == 5


def test_sensor_reader_sensor_mismatch(mock_sensor, monkeypatch):
    sensor_reader = reader.SensorReader(
        port=mock_sensor.port,
        samples=0,  # exit immediately
        sensor="PMSx003",  # match with stubs
        timeout=0.01,  # low to avoid hanging on failure
    )

    mock_sensor.stub(
        name="passive_mode",  # used for validation
        receive_bytes=b"BM\xe1\x00\x00\x01p",
        send_bytes=b"123",  # nonsense
    )

    # https://github.com/pyserial/pyserial/issues/625
    monkeypatch.setattr(
        sensor_reader.serial,
        "flush",
        lambda: None,
    )

    with pytest.raises(reader.UnableToRead) as e:
        with sensor_reader as r:
            list(r())

    assert "failed validation" in str(e.value)


def test_sensor_reader_sensor_no_response(mock_serial):
    sensor_reader = reader.SensorReader(
        port=mock_serial.port,
        samples=0,  # exit immediately
        sensor="PMS3003",  # arbitrary sensor
        timeout=0.01,  # low to avoid hanging on failure
    )

    with pytest.raises(reader.UnableToRead) as e:
        with sensor_reader as r:
            list(r())

    assert "did not respond" in str(e.value)


def test_exit_on_fail_no_error(monkeypatch):
    # prevent the helper exiting the test suite
    monkeypatch.setattr(reader.sys, "exit", lambda: None)
    mock_reader = MockReader()

    with reader.exit_on_fail(mock_reader) as yielded:
        assert yielded == mock_reader

    assert mock_reader.entered
    assert mock_reader.exited


def test_exit_on_fail_error(monkeypatch):
    def sys_exit(*_args):
        raise Exception("exit")

    # prevent the helper exiting the test suite
    monkeypatch.setattr(reader.sys, "exit", sys_exit)
    mock_reader = MockReader(raise_on_enter=True)

    with pytest.raises(Exception) as e:
        with reader.exit_on_fail(mock_reader):
            raise Exception("should not get here")

    assert "exit" in str(e.value)


def test_message_reader():
    message_reader = reader.MessageReader(
        path=captured_data,
        sensor=Sensor["PMS3003"],
    )

    with message_reader:
        values = list(message_reader())

    assert len(values) == 10
