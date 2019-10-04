"""
Serial messages from Plantower sensors

message signature: header, length
- PMS3003 messages are 24b long;
- All other PMSx003 messages are 32b long;
"""

import struct
from typing import Tuple
from pms import WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp
from .base import Message


class PMSx003(Message):
    """Plantower PMSx003 messages"""

    data_records = slice(12)

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
    def _validate(cls, message: bytes, header: bytes, length: int) -> Message:

        # consistency check: bug in message singnature
        assert len(header) == 4, f"wrong header length {len(header)}"
        assert header[:2] == b"BM", f"wrong header start {header}"
        len_payload, = cls._unpack(header[-2:])
        assert length == len(header) + len_payload, f"wrong payload length {length}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header}")
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


class PMS3003(PMSx003):
    """Plantower PMS3003 messages"""

    data_records = slice(6)
