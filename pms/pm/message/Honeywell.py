"""
Serial messages from Honeywell sensors

message signature: header, length
- HPMA115S0 passive mode messages are 8b long
- HPMA115C0 passive mode messages are 16b long
- All active mode messages are 32b long
"""


import struct
from typing import Tuple
from pms import WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp
from .base import BaseMessage


class HPMA115S0(BaseMessage):
    message_header = b"\x40\x05\x04"
    message_length = 8
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
    def _validate(cls, message: bytes, header: bytes, length: int) -> BaseMessage:

        # consistency check: bug in message singnature
        assert len(header) == 3, f"wrong header length {len(header)}"
        assert header[:1] == b"\x40", f"wrong header start {header}"
        assert length in [5, 8, 16], f"wrong payload length {length}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)}")
        checksum = (0x10000 - sum(msg.header) - sum(msg.payload)) % 0x100
        if msg.checksum != checksum:
            raise WrongMessageChecksum(f"message checksum {msg.checksum} != {checksum}")
        if sum(msg.payload) == 0:
            raise SensorWarmingUp(f"message empty: warming up sensor")
        return msg

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f">{len(message)//2}H", message)


class HPMA115C0(HPMA115S0):
    message_length: int = 16
    data_records = slice(4)
