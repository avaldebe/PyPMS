"""
Choose one of the following strategies

Run pytest as a module
$ python3 -m pytest test/

Install locally before testing
$ pip install -e .
$ pytest test/
"""
import os
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
        pytest.param(Sensor.SDS01x, "AAC0D4043A0AA1601DAB", (1236, 2618), id="known good data"),
        pytest.param(
            Sensor.SDS01x,
            "3A0AA1601DABAAC0D4043A0AA1601DAB",
            (1236, 2618),
            id="good data at the end of the buffer",
        ),
    ],
)
def test_decode(sensor, hex, msg, secs=1567201793):
    assert sensor.decode(bytes.fromhex(hex), time=secs) == sensor.Data(secs, *msg)
