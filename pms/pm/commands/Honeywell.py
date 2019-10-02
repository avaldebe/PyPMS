"""
Serial commands for Honeywell sensors

- HPMA115S0/HPMA115C0 use the same commands, but answer to passive_mode have different leghts
"""

from typing import Tuple
from .base import Cmd, BaseCmd
from .. import message


class HPMA(BaseCmd):
    @staticmethod
    def write_cf(cf: int = 0) -> Tuple[bytes, int]:
        """
        Set Customer Adjustment Coefficient

        HPM Series, Particulate Matter Sensors, 32322550 Issue F, Table 4 and Table 6
        https://sensing.honeywell.com/honeywell-sensing-particulate-hpm-series-datasheet-32322550

        cf: 30 ~ 200 (Default, 100)
        """

        assert 30 <= cf <= 200, f"out of range: 30 <= {cf} <= 200"
        h = f"680208{cf:02X}{(0xff8e-cf)%0x100:02X}"
        return Cmd(bytes.fromhex(h), 2)


class HPMA115S0(HPMA):
    """Honeywell HPMA115S0 commands
    
    passive mode message is 8b long (message.HPMA115S0.message_length)
    active mode message is 32b long
    """

    passive_mode = (b"\x68\x01\x20\x77", 2)  # Stop Auto Send
    passive_read = (
        b"\x68\x01\x04\x93",  # Read Particle Measuring Results
        message.HPMA115S0.message_length,
    )
    active_mode = (b"\x68\x01\x40\x57", 2)  # Enable Auto Send
    sleep = (b"\x68\x01\x02\x95", 2)  # Stop Particle Measurement
    wake = (b"\x68\x01\x01\x96", 2)  # Start Particle Measurement
    read_cf = (b"\x68\x01\x10\x87", 5)  # Read Customer Adjustment Coefficient


class HPMA115C0(HPMA):
    """Honeywell HPMA115C0 commands
    
    passive mode message is 16b long (message.HPMA115C0.message_length)
    active mode message is 32b long
    """

    passive_mode = (b"\x68\x01\x20\x77", 2)  # Stop Auto Send
    passive_read = (
        b"\x68\x01\x04\x93",  # Read Particle Measuring Results
        message.HPMA115C0.message_length,
    )
    active_mode = (b"\x68\x01\x40\x57", 2)  # Enable Auto Send
    sleep = (b"\x68\x01\x02\x95", 2)  # Stop Particle Measurement
    wake = (b"\x68\x01\x01\x96", 2)  # Start Particle Measurement
    read_cf = (b"\x68\x01\x10\x87", 5)  # Read Customer Adjustment Coefficient
