"""
Serial messages from Senserion sensors

message signature: header, length
- SPS30 protocol implements byte-stuffing
- After de-stuffing, passive mode messages are 47b long
"""

import struct
from typing import Tuple
from pms import WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp
from .base import Message


class SPS30(Message):
    """NovaFitness SPS30 messages"""

    data_records = slice(10)

    @property
    def header(self) -> bytes:
        return self.message[:5]

    @property
    def payload(self) -> bytes:
        """byte de-stuffing"""
        p = self.message[5:-2]
        for k, v in {
            b"\x7E": b"\x7D\x5E",
            b"\x7D": b"\x7D\x5D",
            b"\x11": b"\x7D\x31",
            b"\x13": b"\x7D\x33",
        }.items():
            if v in p:
                p = p.replace(v, k)
        return p

    @property
    def checksum(self) -> int:
        return self.message[-2]

    @property
    def tail(self) -> int:
        return self.message[-1]

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> Message:

        # consistency check: bug in message singnature
        assert len(header) == 5, f"wrong header length {len(header)}"
        assert header[:2] == b"\x7E\x00", f"wrong header start {header}"
        assert length in [7, 47], f"wrong payload length {length}"
        len_payload = header[-1]
        assert length == len_payload + 7, f"wrong payload length {length}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header}")
        if msg.tail != 0x7E:
            raise WrongMessageFormat(f"message tail: {msg.tail:#x}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)}")
        checksum = 0xFF - (sum(msg.header[1:]) + sum(msg.payload)) % 0x100
        if msg.checksum != checksum:
            raise WrongMessageChecksum(f"message checksum {msg.checksum} != {checksum}")
        if sum(msg.payload) == 0:
            raise SensorWarmingUp(f"message empty: warming up sensor")
        return msg

    @staticmethod
    def _unpack(message: bytes) -> Tuple[float, ...]:
        return struct.unpack(f">{len(message)//4}f", message)
