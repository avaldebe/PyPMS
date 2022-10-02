import pytest

from pms.core import reader


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
