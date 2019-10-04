"""
Serial commands for Honeywell sensors

- HPMA115S0/HPMA115C0 use the same commands, but answer to passive_mode have different leghts
- HPMA115S0 passive mode read message is 8b long
- HPMA115C0 passive mode read message is 16b long
- All active mode read message is 32b long
"""

from .base import Cmd, Commands


class HPMA(Commands):
    @staticmethod
    def read_cf() -> Cmd:
        """Read Customer Adjustment Coefficient"""
        return Cmd(b"\x68\x01\x10\x87", b"\x40\x02\x10", 5)

    @staticmethod
    def write_cf(cf: int = 0) -> Cmd:
        """
        Set Customer Adjustment Coefficient

        HPM Series, Particulate Matter Sensors, 32322550 Issue F, Table 4 and Table 6
        https://sensing.honeywell.com/honeywell-sensing-particulate-hpm-series-datasheet-32322550

        cf: 30 ~ 200 (Default, 100)
        """

        assert 30 <= cf <= 200, f"out of range: 30 <= {cf} <= 200"
        return Cmd(bytes.fromhex(f"680208{cf:02X}{(0xff8e-cf)%0x100:02X}"), b"\xA5\xA5", 2)


HPMA115S0 = HPMA(
    passive_read=Cmd(b"\x68\x01\x04\x93", b"\x40\x05\x04", 8),  # Read Particle Measuring Results
    passive_mode=Cmd(b"\x68\x01\x20\x77", b"\xA5\xA5", 2),  # Stop Auto Send
    active_mode=Cmd(b"\x68\x01\x40\x57", b"\xA5\xA5", 2),  # Enable Auto Send
    sleep=Cmd(b"\x68\x01\x02\x95", b"\xA5\xA5", 2),  # Stop Particle Measurement
    wake=Cmd(b"\x68\x01\x01\x96", b"\xA5\xA5", 2),  # Start Particle Measurement
)

HPMA115C0 = HPMA115S0._replace(
    passive_read=Cmd(b"\x68\x01\x04\x93", b"\x40\x05\x04", 16)  # Read Particle Measuring Results
)
