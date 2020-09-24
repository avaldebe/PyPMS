import os
import pytest

os.environ["LEVEL"] = "DEBUG"
from pms.sensor.novafitness.extra_commands import SDS, HPMA


@pytest.mark.parametrize(
    "cmd,hex,length",
    [
        pytest.param(
            SDS.firmware_version(0xA160),
            "AAB407000000000000000000000000A16008AB",
            10,
            id="SDS firmware",
        ),
        pytest.param(
            SDS.write_id(0xA001, 0xA160),
            "AAB40500000000000000000000A001A160A7AB",
            10,
            id="SDS set device ID",
        ),
        pytest.param(
            SDS.work_period(0),
            "AAB408010000000000000000000000FFFF07AB",
            10,
            id="SDS continuous mode",
        ),
        pytest.param(
            SDS.work_period(1), "AAB408010100000000000000000000FFFF08AB", 10, id="SDS work 1 min"
        ),
        pytest.param(
            SDS.work_period(30), "AAB408011e00000000000000000000FFFF25AB", 10, id="SDS work 30 min"
        ),
        pytest.param(HPMA.read_cf(), "68011087", 5, id="HPMA cf?"),
        pytest.param(HPMA.write_cf(30), "6802081E70", 2, id="HPMA cf 30"),
        pytest.param(HPMA.write_cf(100), "680208642A", 2, id="HPMA cf 100"),
        pytest.param(HPMA.write_cf(200), "680208C8C6", 2, id="HPMA cf 200"),
    ],
)
def test_extra_commands(cmd, hex, length):
    assert cmd.command == bytes.fromhex(hex)
    assert cmd.answer_length == length
