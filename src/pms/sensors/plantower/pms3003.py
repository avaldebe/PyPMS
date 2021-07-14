"""
Plantower PMS3003 sensors
- do not support commands
- messages are 24b long
"""

import struct
from dataclasses import dataclass, field
from typing import Tuple

from pms import SensorWarmingUp, WrongMessageChecksum, WrongMessageFormat

from .. import base

ALIASES = ("G3",)


commands = base.Commands(
    passive_read=base.Cmd(b"", b"\x42\x4D\x00\x14", 24),
    passive_mode=base.Cmd(b"", b"\x42\x4D\x00\x14", 24),
    active_mode=base.Cmd(b"", b"\x42\x4D\x00\x14", 24),
    sleep=base.Cmd(b"", b"\x42\x4D\x00\x14", 24),
    wake=base.Cmd(b"", b"\x42\x4D\x00\x14", 24),
)


class Message(base.Message):
    """Messages from Plantower PMS3003 sensors"""

    data_records = slice(6)

    @property
    def header(self) -> bytes:
        return self.message[:4]

    @property
    def payload(self) -> bytes:
        return self.message[4:-2]

    @property
    def checksum(self) -> int:
        return self._unpack(self.message[-2:])[0]

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> base.Message:

        # consistency check: bug in message singnature
        assert len(header) == 4, f"wrong header length {len(header)}"
        assert header[:2] == b"BM", f"wrong header start {header!r}"
        len_payload = cls._unpack(header[-2:])[0]
        assert length == 4 + len_payload, f"wrong payload length {length} != {4+len_payload}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header!r}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)}")
        checksum = sum(msg.header) + sum(msg.payload)
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
    Plantower PMS3003 sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]

    String formats: pm (default), raw, cf, csv and header
    """

    raw01: int = field(repr=False)
    raw25: int = field(repr=False)
    raw10: int = field(repr=False)
    pm01: int = field(metadata=base.metadata("PM1", "μg/m3", "concentration"))
    pm25: int = field(metadata=base.metadata("PM2.5", "μg/m3", "concentration"))
    pm10: int = field(metadata=base.metadata("PM10", "μg/m3", "concentration"))

    @property
    def raw1(self) -> int:
        return self.raw01

    @property
    def raw2_5(self) -> int:
        return self.raw25

    @property
    def pm1(self) -> int:
        return self.pm01

    @property
    def pm2_5(self) -> int:
        return self.pm25

    @property
    def cf1(self) -> float:
        return self.cf01

    @property
    def cf2_5(self) -> float:
        return self.cf25

    # cfX [1]: pmX/rawX
    @property
    def cf01(self) -> float:
        return self._safe_div(self.pm01, self.raw01)

    @property
    def cf25(self) -> float:
        return self._safe_div(self.pm25, self.raw25)

    @property
    def cf10(self) -> float:
        return self._safe_div(self.pm10, self.raw10)

    @staticmethod
    def _safe_div(x: int, y: int) -> float:
        if y:
            return x / y
        if x == y == 0:  # pragma: no cover
            return 1
        return 0  # pragma: no cover

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"{self.date:%F %T}: PM1 {self.pm01:.1f}, PM2.5 {self.pm25:.1f}, PM10 {self.pm10:.1f} μg/m3"
        if spec == "csv":
            return f"{self.time}, {self.raw01}, {self.raw25}, {self.raw10}, {self.pm01:.1f}, {self.pm25:.1f}, {self.pm10:.1f}"
        if spec == "cf":
            return f"{self.date:%F %T}: CF1 {self.cf01:.0%}, CF2.5 {self.cf25:.0%}, CF10 {self.cf10:.0%}"
        if spec == "raw":
            return (
                f"{self.date:%F %T}: PM1 {self.raw01}, PM2.5 {self.raw25}, PM10 {self.raw10} μg/m3"
            )

        return super().__format__(spec)
