"""
Winsen MH-Z19B sensors
- only support passive reading
- messages are 9b long
"""

import struct
from dataclasses import dataclass, field
from typing import Tuple

from pms import SensorWarmingUp, WrongMessageChecksum, WrongMessageFormat

from .. import base

PREHEAT = 180  # 3 minutes

commands = base.Commands(
    passive_read=base.Cmd(b"\xFF\x01\x86\x00\x00\x00\x00\x00\x79", b"\xFF\x86", 9),
    # same as passive_read for sensor.check
    passive_mode=base.Cmd(b"\xFF\x01\x86\x00\x00\x00\x00\x00\x79", b"\xFF\x86", 9),
    active_mode=base.Cmd(b"", b"", 0),
    sleep=base.Cmd(b"", b"", 0),
    # same as passive_read for sensor.check
    wake=base.Cmd(b"\xFF\x01\x86\x00\x00\x00\x00\x00\x79", b"\xFF\x86", 9),
)


class Message(base.Message):
    """Messages from Winsen MH-Z19B sensors"""

    data_records = slice(1)

    @property
    def header(self) -> bytes:
        return self.message[:2]

    @property
    def payload(self) -> bytes:
        return self.message[2:-1]

    @property
    def checksum(self) -> int:
        return 0x100 - sum(self.message[1:-1]) % 0x100

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> base.Message:

        # consistency check: bug in message singnature
        assert len(header) == 2, f"wrong header length {len(header)}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header!r}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)}")
        checksum = message[-1]
        if msg.checksum != checksum:
            raise WrongMessageChecksum(f"message checksum 0x{msg.checksum:02X} != 0x{checksum:02X}")
        if sum(msg.payload) == 0:
            raise SensorWarmingUp(f"message empty: warming up sensor")
        return msg

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f">{len(message)//2}H", message)


@dataclass(frozen=False)
class ObsData(base.ObsData):
    """
    Winsen MH-Z19B sensor observations

    time                                    measurement time [seconds since epoch]
    CO2                                     CO2 concentration [ppm]

    String formats: co2 (default), csv and header
    """

    CO2: int = field(metadata=base.metadata("CO2", "ppm", "concentration"))

    def __format__(self, spec: str) -> str:
        if spec == "co2":
            return f"{self.date:%F %T}: CO2 {self.CO2} ppm"
        if spec == "csv":
            return f"{self.time}, {self.CO2}"

        return super().__format__(spec)

    def __str__(self):
        return self.__format__("co2")
