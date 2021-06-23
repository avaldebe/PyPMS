from enum import Enum
from typing import Generator, NamedTuple

import pytest

from pms import SensorWarning
from pms.sensor import Sensor


@pytest.mark.parametrize("sensor", [s.name for s in Sensor])
@pytest.mark.parametrize("attr", ["Message", "Data", "Commands"])
def test_sensor_attrs(sensor, attr):
    assert getattr(Sensor[sensor], attr)


@pytest.mark.parametrize("sensor", [s.name for s in Sensor])
@pytest.mark.parametrize("command", "passive_mode passive_read active_mode sleep wake".split())
def test_commands(sensor, command):
    assert Sensor[sensor].command(command)


class RawData(NamedTuple):
    hex: str
    raw: tuple
    id: str = "good data"

    @property
    def msg(self) -> bytes:
        return bytes.fromhex(self.hex)

    @property
    def long_buffer(self) -> "RawData":
        buffer = self.hex * 2
        return self._replace(hex=buffer[6:], id="data at the end of the buffer")


class GoodData(Enum):

    PMSx003 = RawData(
        "424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
        (5, 13, 22, 5, 13, 22, 765, 252, 29, 15, 6, 6),
    )

    PMS3003 = RawData(
        "424d00140051006A007700350046004F33D20F28003F041A",
        (81, 106, 119, 53, 70, 79),
    )

    SDS01x = RawData(
        "AAC0D4043A0AA1601DAB",
        (1236, 2618),
    )

    SDS198 = RawData(
        "AACF0C001600E90510AB",
        (22,),
    )

    HPMA115S0 = RawData(
        "4005040030003156",
        (48, 49),
    )

    HPMA115C0 = RawData(
        "400504003000310032003300000000F1",
        (48, 49, 50, 51),
    )

    SPS30 = RawData(
        "7E0003002842280000422800004228000042280000422800004228000042280000422800004228000042280000B07E",
        (42.0, 42.0, 42.0, 42.0, 42.0, 42.0, 42.0, 42.0, 42.0, 42.0),
        "fake data",
    )

    MCU680 = RawData(
        "5A5A3F0F0835198A01885430D200032BE1004A1A",
        (2101, 6538, 392, 84, 12498, 207841, 74),
    )

    @classmethod
    def test_param(cls) -> Generator[pytest.param, None, None]:  # type: ignore
        for sensor in cls:
            data = sensor.value
            yield pytest.param(sensor.name, data.msg, data.raw, id=f"{sensor.name} {data.id}")
            data = data.long_buffer
            yield pytest.param(sensor.name, data.msg, data.raw, id=f"{sensor.name} {data.id}")

    @classmethod
    def test_obs(cls, secs: int = 1567201793) -> Generator[pytest.param, None, None]:  # type: ignore
        for sensor in cls:
            obs = Sensor[sensor.name].decode(sensor.value.msg, time=secs)
            yield pytest.param(obs, id=sensor.name)


@pytest.mark.parametrize("sensor,msg,raw", [test for test in GoodData.test_param()])
def test_decode(sensor, msg, raw, secs=1567201793):
    assert Sensor[sensor].decode(msg, time=secs) == Sensor[sensor].Data(secs, *raw)


@pytest.mark.parametrize("obs", GoodData.test_obs())
def test_obs_prop(obs):
    prop = dict(
        pm01=lambda x: x.pm01 == x.pm1,
        pm25=lambda x: x.pm25 == x.pm2_5,
        pm04=lambda x: x.pm04 == x.pm4,
        raw01=lambda x: x.raw01 == x.raw1,
        raw25=lambda x: x.raw25 == x.raw2_5,
        cf01=lambda x: x.cf01 == x.cf1,
        cf25=lambda x: x.cf25 == x.cf2_5,
    )
    for field, check in prop.items():
        if getattr(obs, field, None) is None:
            continue
        assert check(obs)


@pytest.mark.parametrize(
    "sensor,hex,error",
    [
        pytest.param(
            "PMSx003",
            "424d001c0000000a00200000000a002000000000000000000000000097000196",
            "inconsistent obs: PM10=32 and N0.3=0.0",
            id="PMSx003",
        ),
        pytest.param(
            "PMS5003T",
            "424d001c0000000a00200000000a002000000000000000000000000097000196",
            "inconsistent obs: PM10=32 and N0.3=0.0",
            id="PMS5003T",
        ),
        pytest.param(
            "PMS5003S",
            "424d001c0000000a00200000000a002000000000000000000000000097000196",
            "inconsistent obs: PM10=32 and N0.3=0.0",
            id="PMS5003S",
        ),
        pytest.param(
            "PMS5003ST",
            "424d00240000000a00200000000a002000000000000000000000000000000000000000009700019E",
            "inconsistent obs: PM10=32 and N0.3=0.0",
            id="PMS5003ST",
        ),
    ],
)
def test_decode_error(sensor, hex, error, secs=1567201793):
    with pytest.raises(SensorWarning) as e:
        Sensor[sensor].decode(bytes.fromhex(hex), time=secs)
    assert str(e.value) == error


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
