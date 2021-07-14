"""
NovaFitness SDS011, SDS018 and SDS021 sensors
- messages are 10b long
"""

import struct
from dataclasses import dataclass, field
from typing import Tuple

from pms import SensorWarmingUp, WrongMessageChecksum, WrongMessageFormat

from .. import base

ALIASES = ("SDS011", "SDS018", "SDS021")


commands = base.Commands(
    passive_read=base.Cmd(
        b"\xAA\xB4\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x02\xAB",
        b"\xAA\xC0",
        10,
    ),
    passive_mode=base.Cmd(
        b"\xAA\xB4\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x02\xAB",
        b"\xAA\xC5",
        10,
    ),
    active_mode=base.Cmd(
        b"\xAA\xB4\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x01\xAB",
        b"\xAA\xC5",
        10,
    ),
    sleep=base.Cmd(
        b"\xAA\xB4\x06\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x05\xAB",
        b"\xAA\xC5",
        10,
    ),
    wake=base.Cmd(
        b"\xAA\xB4\x06\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x06\xAB",
        b"\xAA\xC5",
        10,
    ),
)


class Message(base.Message):
    """Messages from NovaFitness SDS011, SDS018 and SDS021 sensors"""

    data_records = slice(2)

    @property
    def header(self) -> bytes:
        return self.message[:2]

    @property
    def payload(self) -> bytes:
        return self.message[2:-2]

    @property
    def checksum(self) -> int:
        return self.message[-2]

    @property
    def tail(self) -> int:
        return self.message[-1]

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> base.Message:

        # consistency check: bug in message singnature
        assert len(header) == 2, f"wrong header length {len(header)}"
        assert header[:1] == b"\xAA", f"wrong header start {header!r}"
        assert length == 10, f"wrong payload length {length} != 10"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header!r}")
        if msg.tail != 0xAB:
            raise WrongMessageFormat(f"message tail: {msg.tail:#x}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)}")
        checksum = sum(msg.payload) % 0x100
        if msg.checksum != checksum:
            raise WrongMessageChecksum(f"message checksum {msg.checksum} != {checksum}")
        if sum(msg.payload[:-2]) == 0:
            raise SensorWarmingUp(f"message empty: warming up sensor")
        return msg

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f"<{len(message)//2}H", message)


@dataclass(frozen=False)
class ObsData(base.ObsData):
    """
    NovaFitness SDS011, SDS018 and SDS021 sensor observations

    time                                    measurement time [seconds since epoch]
    pm25, pm10                              PM2.5, PM10 [μg/m3]

    String formats: pm (default), csv and header
    """

    pm25: float = field(metadata=base.metadata("PM2.5", "μg/m3", "concentration"))
    pm10: float = field(metadata=base.metadata("PM10", "μg/m3", "concentration"))

    @property
    def pm2_5(self) -> float:
        return self.pm25

    def __post_init__(self):
        """Convert from 0.1 μg/m3 to μg/m3"""
        self.pm25 /= 10
        self.pm10 /= 10

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"{self.date:%F %T}: PM2.5 {self.pm25:.1f}, PM10 {self.pm10:.1f} μg/m3"
        if spec == "csv":
            return f"{self.time}, {self.pm25:.1f}, {self.pm10:.1f}"
        if spec == "":
            return str(self)

        return super().__format__(spec)
