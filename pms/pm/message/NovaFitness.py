"""
Serial messages from NovaFitness sensors

message signature: header, length
- All SDS01x/SDS198 messages are 10b long.
"""

import struct
from typing import Tuple
from pms import WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp
from .base import Message


class SDS01x(Message):
    """NovaFitness SDS01x messages"""

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
    def _validate(cls, message: bytes, header: bytes, length: int) -> Message:

        # consistency check: bug in message singnature
        assert len(header) == 2, f"wrong header length {len(header)}"
        assert header[:1] == b"\xAA", f"wrong header start {header}"
        assert length == 10, f"wrong payload length {length}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header}")
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


class SDS198(SDS01x):
    """NovaFitness SDS198 messages"""

    data_records = slice(1, 2)
