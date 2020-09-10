from .base import Cmd


class SDS:
    """Additional commands for NovaFitness sensors

    Laser Dust Sensor Control Protocol V1.3
    https://learn.watterott.com/sensors/sds011/sds011_protocol.pdf
    """

    @staticmethod
    def _msg(cmd: int, payload: str, device: int = 0xFFFF) -> bytes:
        assert 0 <= cmd <= 0xFF, f"command id out of range: 0 <= {cmd} <= 0xFF"
        assert 0 <= device <= 0xFFFF, f"device id out of range: 0 <= {device} <= 0xFFFF"
        checksum = sum(bytes.fromhex(payload)) + device // 0x100 + device % 0x100
        return bytes.fromhex(f"AA{cmd:02X}{payload}{device:04X}{checksum%0x100:02X}AB")

    @classmethod
    def write_id(cls, new_id: int, device: int = 0xFFFF) -> Cmd:
        """Protocol V1.3, section 3) Set Device ID

        The setting is still effective after power off [Factory default has set a unique ID]
        """
        return Cmd(cls._msg(0xB4, f"0500000000000000000000{new_id:02X}", device), b"\xAA\xC0", 10)

    @classmethod
    def work_period(cls, minutes: int = 0, device: int = 0xFFFF) -> Cmd:
        """Protocol V1.3, section 5) Set working period

        The setting is still effective after power off [factory default is continuous measurement]
        The sensor works periodically and reports the latest data.

        0 minute: continuous mode (default), i.e. report every 1 second
        1-30 minutes: sample for 30 secors and sleep the rest of the period
        """

        assert 0 <= minutes <= 30, f"minutes out of range: 0 <= {minutes} <= 30"
        return Cmd(
            cls._msg(0xB4, f"0801{minutes:02X}00000000000000000000", device), b"\xAA\xC0", 10
        )

    @classmethod
    def firmware_version(cls, device: int = 0xFFFF) -> Cmd:
        """Protocol V1.3, 6) Check firmware version"""
        return Cmd(cls._msg(0xB4, "07000000000000000000000000", device), b"\xAA\xC0", 10)


class HPMA:
    """Additional commands for Honeywell sensors

    HPM Series, Particulate Matter Sensors, 32322550 Issue F
    https://sensing.honeywell.com/honeywell-sensing-particulate-hpm-series-datasheet-32322550
    """

    @staticmethod
    def read_cf() -> Cmd:
        """Read Customer Adjustment Coefficient

        HPM Series, Table 4 and Table 6
        """
        return Cmd(b"\x68\x01\x10\x87", b"\x40\x02\x10", 5)

    @staticmethod
    def write_cf(cf: int = 0) -> Cmd:
        """Set Customer Adjustment Coefficient

        HPM Series, Table 4 and Table 6
        cf: 30 ~ 200 (Default, 100)
        """

        assert 30 <= cf <= 200, f"out of range: 30 <= {cf} <= 200"
        return Cmd(bytes.fromhex(f"680208{cf:02X}{(0xff8e-cf)%0x100:02X}"), b"\xA5\xA5", 2)
