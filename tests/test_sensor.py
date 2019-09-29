"""
Choose one of the following strategies

Run pytest as a module
$ python3 -m pytest test/

Install locally before testing
$ pip install -e .
$ pytest test/
"""
import os, time
import pytest

try:
    os.environ["LEVEL"] = "DEBUG"
    from pms.sensor import Sensor
    from pms import SensorWarning
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize(
    "sensor,hex,msg",
    [
        pytest.param(
            Sensor.PMSx003,
            "424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
            (5, 13, 22, 5, 13, 22, 765, 252, 29, 15, 6, 6),
            id="known good data",
        ),
        pytest.param(
            Sensor.PMSx003,
            "02fd00fc001d000f00060006970003c5424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
            (5, 13, 22, 5, 13, 22, 765, 252, 29, 15, 6, 6),
            id="good data at the end of the buffer",
        ),
        pytest.param(
            Sensor.PMS3003,
            "424d00140051006A007700350046004F33D20F28003F041A",
            (81, 106, 119, 53, 70, 79),
            id="known good data",
        ),
        pytest.param(
            Sensor.PMS3003,
            "33D20F28003F041A424d00140051006A007700350046004F33D20F28003F041A",
            (81, 106, 119, 53, 70, 79),
            id="good data at the end of the buffer",
        ),
        pytest.param(Sensor.SDS011, "AAC0D4043A0AA1601DAB", (1236, 2618), id="known good data"),
        pytest.param(
            Sensor.SDS011,
            "3A0AA1601DABAAC0D4043A0AA1601DAB",
            (1236, 2618),
            id="good data at the end of the buffer",
        ),
    ],
)
def test_decode(sensor, hex, msg, secs=1567201793):
    assert sensor.decode(bytes.fromhex(hex), time=secs) == sensor.Data(secs, *msg)


@pytest.mark.parametrize(
    "sensor,hex,error",
    [
        pytest.param(
            Sensor.PMSx003, "424d001c0005000d0016", "message length: 10", id="short message"
        ),
        pytest.param(
            Sensor.PMSx003,
            "424d00000005000d00160005000d001602fd00fc001d000f00060006970003a9",
            r"message header: b'BM\x00\x00'",
            id="wrong header",
        ),
        pytest.param(
            Sensor.PMSx003,
            "424d001c0005000d00160005000d001602fd00fc001d000f0006000697000000",
            "message checksum 0 != 965",
            id="wrong checksum",
        ),
        pytest.param(
            Sensor.PMSx003,
            "424d001c000000000000000000000000000000000000000000000000000000ab",
            "message empty: warming up sensor",
            id="empty message",
        ),
        pytest.param(
            Sensor.PMS3003, "424d00140051006A0077", "message length: 10", id="short message"
        ),
        pytest.param(
            Sensor.PMS3003,
            "424d00000051006A007700350046004F33D20F28003F0406",
            r"message header: b'BM\x00\x00'",
            id="wrong header",
        ),
        pytest.param(
            Sensor.PMS3003,
            "424d00140051006A007700350046004F33D20F28003F0000",
            "message checksum 0 != 1050",
            id="wrong checksum",
        ),
        pytest.param(
            Sensor.PMS3003,
            "424d001400000000000000000000000000000000000000a3",
            "message empty: warming up sensor",
            id="empty message",
        ),
        pytest.param(Sensor.SDS011, "AAC0D4041DAB", "message length: 6", id="short message"),
        pytest.param(
            Sensor.SDS011, "ABC0D4043A0AA1601DAA", r"message header: b'\xab\xc0'", id="wrong header"
        ),
        pytest.param(Sensor.SDS011, "AAC0D4043A0AA1601DAA", "message tail: 0xaa", id="wrong tail"),
        pytest.param(
            Sensor.SDS011, "AAC0D4043A0AA16000AB", "message checksum 0 != 29", id="wrong checksum"
        ),
        pytest.param(
            Sensor.SDS011,
            "AAC000000000000000AB",
            "message empty: warming up sensor",
            id="empty message",
        ),
    ],
)
def test_decode_error(sensor, hex, error, secs=1567201793):
    with pytest.raises(SensorWarning) as e:
        sensor.decode(bytes.fromhex(hex), time=secs)
    assert str(e.value) == error
