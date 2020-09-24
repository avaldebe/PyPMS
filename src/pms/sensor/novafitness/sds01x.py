"""
NovaFitness SDS011, SDS018 and SDS021 sensors
- messages are 10b long
"""

from dataclasses import dataclass, field
from typing import Tuple
import struct

from pms import WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp
from pms.sensor import base

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
    """SDS01x observations

    time                                    measurement time [seconds since epoch]
    raw25, raw10                            PM2.5*10, PM10*10 [ug/m3]
    """

    pm25: float = field(metadata=base.metadata("PM2.5", "ug/m3", "concentration"))
    pm10: float = field(metadata=base.metadata("PM10", "ug/m3", "concentration"))

    def __post_init__(self):
        """Convert from 0.1 ug/m3 to ug/m3"""
        self.pm25 /= 10
        self.pm10 /= 10

    def __format__(self, spec: str) -> str:
        if spec == "header":
            return super().__format__(spec)
        if spec == "pm":
            return f"{self.date:%F %T}: PM2.5 {self.pm25:.1f}, PM10 {self.pm10:.1f} ug/m3"
        if spec == "csv":
            return f"{self.time}, {self.pm25:.1f}, {self.pm10:.1f}"
        raise ValueError(  # pragma: no cover
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
