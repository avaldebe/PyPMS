import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger

from pms import SensorWarmingUp, SensorWarning
from pms.core.reader import SensorReader, UnableToRead
from pms.core.sensor import Sensor


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def mock_sleep(monkeypatch):
    def sleep(seconds):
        sleep.slept_for += seconds

    sleep.slept_for = 0

    monkeypatch.setattr("pms.core.reader.time.sleep", sleep)
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


@pytest.fixture
def mock_sensor_warm_up(mock_serial):
    def passive_read(n):
        if n == 1:
            # first return a "0" payload ("warming up")
            return (
                b"BM\x00\x1c"  # expected header
                + b"\0" * 26  # payload (to total 32 bytes)
                + b"\x00\xab"  # checksum
            )
        else:
            # then behave like the original stub again
            return (
                b"BM\x00\x1c"  # expected header
                + b".........................."  # payload
                + b"\x05W"  # checksum
            )

    mock_serial.stub(
        name="passive_read",
        receive_bytes=b"BM\xe2\x00\x00\x01q",
        send_fn=passive_read,
    )


@pytest.fixture
def mock_sensor_temp_failure(mock_serial):
    def passive_read(n):
        if n == 1:
            # first return garbage data (bad checksum)
            return (
                b"BM\x00\x1c"  # expected header
                + b"\0" * 26  # payload (to total 32 bytes)
                + b"\x00\xff"  # checksum
            )
        else:
            # then behave like the original stub again
            return (
                b"BM\x00\x1c"  # expected header
                + b".........................."  # payload
                + b"\x05W"  # checksum
            )

    mock_serial.stub(
        name="passive_read",
        receive_bytes=b"BM\xe2\x00\x00\x01q",
        send_fn=passive_read,
    )


@pytest.fixture()
def reader(monkeypatch, mock_sensor) -> SensorReader:
    reader = SensorReader(
        "PMSx003",  # match with stubs
        mock_sensor.port,
        samples=0,  # exit immediately
        interval=None,
        max_retries=None,
        timeout=0.01,  # low to avoid hanging on failure
    )

    # https://github.com/pyserial/pyserial/issues/625
    monkeypatch.setattr(reader.serial, "flush", lambda: None)

    reader.pre_heat = 0  # disable any preheat

    return reader


def test_reader(reader: SensorReader, mock_serial):
    with reader:
        obs = tuple(reader())

    # check warm up happened
    assert mock_serial.stubs["wake"].called
    assert mock_serial.stubs["passive_mode"].called

    # check data was read
    assert len(obs) == 1
    assert obs[0].pm10 == 11822  # type:ignore

    # check sleep happened
    assert mock_serial.stubs["sleep"].called


def test_reader_sleep(reader: SensorReader, mock_sleep):
    reader.samples = 2  # try to read twice
    reader.interval = 5  # sleep between samples

    with reader:
        obs = tuple(reader())

    # check we read twice
    assert len(obs) == 2

    # check we slept between reads
    assert 0 < mock_sleep.slept_for < 5


def test_reader_closed(reader: SensorReader):
    obs = tuple(reader())
    assert len(obs) == 0


def test_reader_preheat(reader: SensorReader, mock_sleep):
    reader.pre_heat = 5  # override pre heat duration

    with reader:
        pass

    # check we slept between reads
    assert mock_sleep.slept_for == 5


def test_reader_warm_up(reader: SensorReader, mock_sleep, mock_sensor_warm_up):
    with reader:
        obs = tuple(reader())

    # check we slept for warm up
    assert mock_sleep.slept_for == 5
    assert len(obs) == 1


def test_reader_warm_up_exhaust_retries(reader: SensorReader, mock_sensor_warm_up):
    reader.max_retries = 0

    with reader:
        with pytest.raises(SensorWarmingUp):
            next(reader())


def test_reader_temp_failure(reader: SensorReader, mock_serial, mock_sensor_temp_failure):
    with reader:
        obs = tuple(reader())

    # check one sample still acquired
    assert len(obs) == 1

    # check two samples were attempted
    assert mock_serial.stubs["passive_read"].calls == 2


def test_reader_temp_failure_exhaust_retries(reader: SensorReader, mock_sensor_temp_failure):
    reader.max_retries = 0

    with reader:
        with pytest.raises(SensorWarning):
            next(reader())


def test_reader_sensor_mismatch(reader: SensorReader, mock_serial):
    mock_serial.stub(
        name="passive_mode",  # used for validation
        receive_bytes=b"BM\xe1\x00\x00\x01p",
        send_bytes=b"123",  # nonsense
    )

    with pytest.raises(UnableToRead) as e:
        with reader as r:  # noqa: F841
            pass

    assert "failed validation" in str(e.value)


def test_reader_sensor_no_response(reader: SensorReader):
    reader.sensor = Sensor["PMS3003"]  # wrong sensor

    with pytest.raises(UnableToRead) as e:
        with reader:
            pass

    assert "did not respond" in str(e.value)


def test_logging(reader: SensorReader, capfd, caplog):
    with reader:
        obs = tuple(reader())

    # check data was read
    assert len(obs) == 1
    assert obs[0].pm10 == 11822  # type:ignore

    # check no logs output
    assert caplog.text == ""
