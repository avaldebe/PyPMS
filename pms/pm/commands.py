"""
Serial commands for
- Plantower PMSx003 PM1/PM2.5/PM10 sensors
- NovaFitness SDS01x PM2.5/PM10 sensors
- The SDS198 PM100 sensor is not supported
"""

from enum import Enum
from typing import Tuple, NamedTuple
from . import message


class PMSx003(Enum):
    """Plantower PMSx003 commands"""

    passive_mode = (b"\x42\x4D\xE1\x00\x00\x01\x70", 8)
    passive_read = (b"\x42\x4D\xE2\x00\x00\x01\x71", message.PMSx003.message_length)
    active_mode = (b"\x42\x4D\xE1\x00\x01\x01\x71", message.PMSx003.message_length)
    sleep = (b"\x42\x4D\xE4\x00\x00\x01\x73", 8)
    wake = (b"\x42\x4D\xE4\x00\x01\x01\x74", message.PMSx003.message_length)

    @property
    def command(self) -> bytes:
        return self.value[0]

    @property
    def answer_length(self) -> int:
        return self.value[1]


class PMS3003(Enum):
    """Plantower PMS3003 commands"""

    active_read = (b"", message.PMS3003.message_length)
    passive_read = passive_mode = active_mode = sleep = wake = active_read

    @property
    def command(self) -> bytes:
        return self.value[0]

    @property
    def answer_length(self) -> int:
        return self.value[1]


class _Cmd(NamedTuple):
    command: bytes
    answer_length: int


class SDS01x(Enum):
    """NovaFitness SDS01x commands"""

    passive_mode = (
        b"\xAA\xB4\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x02\xAB",
        message.SDS01x.message_length,
    )
    passive_read = (
        b"\xAA\xB4\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x02\xAB",
        message.SDS01x.message_length,
    )
    active_mode = (
        b"\xAA\xB4\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x01\xAB",
        message.SDS01x.message_length,
    )
    sleep = (
        b"\xAA\xB4\x06\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x05\xAB",
        message.SDS01x.message_length,
    )
    wake = (
        b"\xAA\xB4\x06\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x06\xAB",
        message.SDS01x.message_length,
    )
    firmware_version = (
        b"\xAA\xB4\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x05\xAB",
        message.SDS01x.message_length,
    )

    @property
    def command(self) -> bytes:
        return self.value[0]

    @property
    def answer_length(self) -> int:
        return self.value[1]

    @staticmethod
    def work_period(minutes: int = 0) -> Tuple[bytes, int]:
        """"
        "Laser Dust Sensor Control Protocol V1.3", section 5) Set working period
        https://learn.watterott.com/sensors/sds011/sds011_protocol.pdf

        The setting is still effective after power off [factory default is continuous measurement]
        The sensor works periodically and reports the latest data.

        0 minute: continuous mode (default), i.e. report every 1 second
        1-30 minutes: sample for 30 secors and sleep the rest of the period
        """

        assert 0 <= minutes <= 30, f"out of range: 0 <= {minutes} <= 30"
        hex = f"AAB40801{minutes:02X}00000000000000000000FFFF{minutes+7:02X}AB"
        return _Cmd(bytes.fromhex(hex), message.SDS01x.message_length)
