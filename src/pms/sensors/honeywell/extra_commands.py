"""Additional commands for Honeywell sensors

HPM Series, Particulate Matter Sensors, 32322550 Issue F
https://sensing.honeywell.com/honeywell-sensing-particulate-hpm-series-datasheet-32322550
"""

from ..base import Cmd


def read_cf() -> Cmd:
    """Read Customer Adjustment Coefficient

    HPM Series, Table 4 and Table 6
    """
    return Cmd(b"\x68\x01\x10\x87", b"\x40\x02\x10", 5)


def write_cf(cf: int = 0) -> Cmd:
    """Set Customer Adjustment Coefficient

    HPM Series, Table 4 and Table 6
    cf: 30 ~ 200 (Default, 100)
    """

    assert 30 <= cf <= 200, f"out of range: 30 <= {cf} <= 200"
    return Cmd(bytes.fromhex(f"680208{cf:02X}{(0xff8e-cf)%0x100:02X}"), b"\xA5\xA5", 2)
