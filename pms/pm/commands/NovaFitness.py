"""
Serial commands NovaFitness sensors

- SDS01x/SDS198 have the same commands
- Support active/passive mode and sleep/wake
- Also support periodic wake/sleep cycles
"""

from typing import Tuple, NamedTuple
from .base import Cmd, BaseCmd
from .. import message


class SDS01x(BaseCmd):
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
        return Cmd(bytes.fromhex(hex), message.SDS01x.message_length)


# NovaFitness SDS198 commands are the same as the SDS011/SDS018/SDS021
SDS198 = SDS01x
