import os
import pytest

os.environ["LEVEL"] = "DEBUG"
from pms.sensor import Sensor
from pms import SensorWarning


@pytest.mark.parametrize("sensor", [s.name for s in Sensor])
@pytest.mark.parametrize("attr", ["Message", "Data", "Commands"])
def test_sensor_attrs(sensor, attr):
    assert getattr(Sensor[sensor], attr)


@pytest.mark.parametrize("sensor", [s.name for s in Sensor])
@pytest.mark.parametrize("command", "passive_mode passive_read active_mode sleep wake".split())
def test_commands(sensor, command):
    assert Sensor[sensor].command(command)


@pytest.mark.parametrize(
    "sensor,hex,msg",
    [
        pytest.param(
            "PMSx003",
            "424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
            (5, 13, 22, 5, 13, 22, 765, 252, 29, 15, 6, 6),
            id="PMSx003 good data",
        ),
        pytest.param(
            "PMSx003",
            "02fd00fc001d000f00060006970003c5424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
            (5, 13, 22, 5, 13, 22, 765, 252, 29, 15, 6, 6),
            id="PMSx003 data at the end of the buffer",
        ),
        pytest.param(
            "PMS3003",
            "424d00140051006A007700350046004F33D20F28003F041A",
            (81, 106, 119, 53, 70, 79),
            id="PMS3003 good data",
        ),
        pytest.param(
            "PMS3003",
            "33D20F28003F041A424d00140051006A007700350046004F33D20F28003F041A",
            (81, 106, 119, 53, 70, 79),
            id="PMS3003 data at the end of the buffer",
        ),
        pytest.param("SDS01x", "AAC0D4043A0AA1601DAB", (1236, 2618), id="SDS01x good data"),
        pytest.param(
            "SDS01x",
            "3A0AA1601DABAAC0D4043A0AA1601DAB",
            (1236, 2618),
            id="SDS01x data at the end of the buffer",
        ),
        pytest.param("SDS198", "AACF00006400e90552AB", (100,), id="SDS198 good data"),
        pytest.param("HPMA115S0", "4005040030003156", (48, 49), id="HPMA115S0 good data"),
        pytest.param(
            "HPMA115S0",
            "A5A54005040030003156",
            (48, 49),
            id="HPMA115S0 data at the end of the buffer",
        ),
        pytest.param(
            "HPMA115C0",
            "400504003000310032003300000000F1",
            (48, 49, 50, 51),
            id="HPMA115C0 good data",
        ),
        pytest.param(
            "HPMA115C0",
            "A5A5400504003000310032003300000000F1",
            (48, 49, 50, 51),
            id="HPMA115C0 data at the end of the buffer",
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
        pytest.param("HPMA115S0", "passive_read", "68010493", 8, id="HPMA115S0 read"),
        pytest.param("HPMA115S0", "sleep", "68010295", 2, id="HPMA115S0 sleep"),
        pytest.param("HPMA115S0", "wake", "68010196", 2, id="HPMA115S0 wake"),
        pytest.param("HPMA115C0", "passive_read", "68010493", 16, id="HPMA115C0 read"),
    ],
)
def test_command(sensor, command, hex, length):
    cmd = Sensor[sensor].command(command)
    assert cmd.command == bytes.fromhex(hex)
    assert cmd.answer_length == length
