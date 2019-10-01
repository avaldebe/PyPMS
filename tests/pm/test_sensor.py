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
    from pms.pm.sensor import Sensor
    from pms import SensorWarning
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize("sensor", [s.name for s in Sensor])
@pytest.mark.parametrize("attr", ["Message", "Data", "Commands"])
def test_sensor_attrs(sensor, attr):
    assert getattr(Sensor[sensor], attr)


@pytest.mark.parametrize(
    "sensor,hex,msg",
    [
        pytest.param(
            "PMSx003",
            "424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
            (5, 13, 22, 5, 13, 22, 765, 252, 29, 15, 6, 6),
            id="known good data",
        ),
        pytest.param(
            "PMSx003",
            "02fd00fc001d000f00060006970003c5424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
            (5, 13, 22, 5, 13, 22, 765, 252, 29, 15, 6, 6),
            id="good data at the end of the buffer",
        ),
        pytest.param(
            "PMS3003",
            "424d00140051006A007700350046004F33D20F28003F041A",
            (81, 106, 119, 53, 70, 79),
            id="known good data",
        ),
        pytest.param(
            "PMS3003",
            "33D20F28003F041A424d00140051006A007700350046004F33D20F28003F041A",
            (81, 106, 119, 53, 70, 79),
            id="good data at the end of the buffer",
        ),
        pytest.param("SDS01x", "AAC0D4043A0AA1601DAB", (1236, 2618), id="known good data"),
        pytest.param(
            "SDS01x",
            "3A0AA1601DABAAC0D4043A0AA1601DAB",
            (1236, 2618),
            id="good data at the end of the buffer",
        ),
    ],
)
def test_decode(sensor, hex, msg, secs=1567201793):
    assert Sensor[sensor].decode(bytes.fromhex(hex), time=secs) == Sensor[sensor].Data(secs, *msg)


@pytest.mark.parametrize(
    "sensor,command,hex,length",
    [
        pytest.param("PMSx003", "passive_mode", "424DE100000170", 8, id="PMSx003 passive"),
        pytest.param("PMSx003", "passive_read", "424DE200000171", 32, id="PMSx003 read"),
        pytest.param("PMSx003", "sleep", "424DE400000173", 8, id="PMSx003 sleep"),
        pytest.param("PMSx003", "wake", "424DE400010174", 32, id="PMSx003 wake"),
        pytest.param("PMS3003", "passive_mode", "", 24, id="PMS3003 passive"),
        pytest.param(
            "SDS01x",
            "passive_mode",
            "AAB402010100000000000000000000FFFF02AB",
            10,
            id="SDS01x passive",
        ),
        pytest.param(
            "SDS01x", "passive_read", "AAB404000000000000000000000000FFFF02AB", 10, id="SDS01x read"
        ),
        pytest.param(
            "SDS01x", "sleep", "AAB406010000000000000000000000FFFF05AB", 10, id="SDS01x sleep"
        ),
        pytest.param(
            "SDS01x", "wake", "AAB406010100000000000000000000FFFF06AB", 10, id="SDS01x wake"
        ),
    ],
)
def test_command(sensor, command, hex, length):
    cmd = Sensor[sensor].command(command)
    assert cmd.command == bytes.fromhex(hex)
    assert cmd.answer_length == length


@pytest.mark.parametrize(
    "minutes,hex,length",
    [
        pytest.param(0, "AAB408010000000000000000000000FFFF07AB", 10, id="continuous mode"),
        pytest.param(1, "AAB408010100000000000000000000FFFF08AB", 10, id="1 min"),
        pytest.param(30, "AAB408011e00000000000000000000FFFF25AB", 10, id="30 min"),
    ],
)
def test_command_work_period(minutes, hex, length, sensor="SDS01x"):
    cmd = Sensor[sensor].Commands.work_period(minutes)
    assert cmd.command == bytes.fromhex(hex)
    assert cmd.answer_length == length
