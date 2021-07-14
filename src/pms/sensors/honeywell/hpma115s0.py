"""
Honeywell HPMA115S0 sensors
- passive mode messages are 8b long
- active mode messages are 32b long
"""

import struct
from dataclasses import dataclass, field
from typing import Tuple

from pms import SensorWarmingUp, WrongMessageChecksum, WrongMessageFormat

from .. import base

commands = base.Commands(
    passive_read=base.Cmd(  # Read Particle Measuring Results
        b"\x68\x01\x04\x93", b"\x40\x05\x04", 8
    ),
    passive_mode=base.Cmd(b"\x68\x01\x20\x77", b"\xA5\xA5", 2),  # Stop Auto Send
    active_mode=base.Cmd(b"\x68\x01\x40\x57", b"\xA5\xA5", 2),  # Enable Auto Send
    sleep=base.Cmd(b"\x68\x01\x02\x95", b"\xA5\xA5", 2),  # Stop Particle Measurement
    wake=base.Cmd(b"\x68\x01\x01\x96", b"\xA5\xA5", 2),  # Start Particle Measurement
)


class Message(base.Message):
    """Messages from Honeywell HPMA115S0 sensors"""

    data_records = slice(2)

    @property
    def header(self) -> bytes:
        return self.message[:3]

    @property
    def payload(self) -> bytes:
        return self.message[3:-1]

    @property
    def checksum(self) -> int:
        return self.message[-1]

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> base.Message:

        # consistency check: bug in message singnature
        assert len(header) == 3, f"wrong header length {len(header)}"
        assert header[:1] == b"\x40", f"wrong header start {header!r}"
        assert length in [5, 8, 16], f"wrong payload length {length}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header!r}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)} != {length}")
        checksum = (0x10000 - sum(msg.header) - sum(msg.payload)) % 0x100
        if msg.checksum != checksum:
            raise WrongMessageChecksum(f"message checksum {msg.checksum} != {checksum}")
        if sum(msg.payload) == 0:
            raise SensorWarmingUp(f"message empty: warming up sensor")
        return msg

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f">{len(message)//2}H", message)


@dataclass(frozen=False)
class ObsData(base.ObsData):
    """
    Honeywell HPMA115S0 sensor observations

    time                                    measurement time [seconds since epoch]
    pm25, pm10                              PM2.5, PM10 [μg/m3]

    String formats: pm (default), csv and header
    """

    pm25: int = field(metadata=base.metadata("PM2.5", "μg/m3", "concentration"))
    pm10: int = field(metadata=base.metadata("PM10", "μg/m3", "concentration"))

    @property
    def pm2_5(self) -> int:
        return self.pm25

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"{self.date:%F %T}: PM2.5 {self.pm25:.1f}, PM10 {self.pm10:.1f} μg/m3"
        if spec == "csv":
            return f"{self.time}, {self.pm25:.1f}, {self.pm10:.1f}"
        if spec == "":
            return str(self)

        return super().__format__(spec)
