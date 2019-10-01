"""
Serial messages from
- Plantower PMSx003 PM1/PM2.5/PM10 sensors
- NovaFitness SDS01x PM2.5/PM10 sensors
- The SDS198 PM100 sensor is not supported

message signature: header, length
- PMS3003 messages are 24b long;
- All other PMSx003 messages are 32b long;
- All SDS01x messages are 10b long.
"""

import struct
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from pms import logger, WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp


class BaseMessage(ABC):
    def __init__(self, message: bytes) -> None:
        logger.debug(f"message hex: {message.hex()}")
        self.message = message

    @classmethod
    def unpack(cls, message: bytes, header: bytes, length: int) -> Tuple[int, ...]:
        try:
            # validate full message
            msg = cls._validate(message, header, length)
        except WrongMessageFormat as e:
            # search last complete message on buffer
            start = message.rfind(header, 0, 4 - length)
            if start < 0:  # No match found
                raise
            # validate last complete message
            msg = cls._validate(message[start : start + length], header, length)

        # data: unpacked payload
        payload = cls._unpack(msg.payload)
        logger.debug(f"message payload: {payload}")
        return payload

    @classmethod
    def decode(cls, message: bytes) -> Tuple[int, ...]:
        header: bytes = cls.message_header  # type: ignore
        length: int = cls.message_length  # type: ignore
        return cls.unpack(message, header, length)[cls.data_records]  # type: ignore

    @property
    @classmethod
    @abstractmethod
    def message_header(cls) -> bytes:
        pass

    @property
    @classmethod
    @abstractmethod
    def message_length(cls) -> int:
        pass

    @property
    @classmethod
    @abstractmethod
    def data_records(cls) -> slice:
        pass

    @property
    @abstractmethod
    def header(self) -> bytes:
        pass

    @property
    @abstractmethod
    def payload(self) -> bytes:
        pass

    @property
    @abstractmethod
    def checksum(self) -> int:
        pass

    @classmethod
    @abstractmethod
    def _validate(self, message: bytes, header: bytes, length: int) -> "BaseMessage":
        pass

    @staticmethod
    @abstractmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        pass


class PMSx003(BaseMessage):
    """Plantower PMSx003 messages"""

    message_header = b"\x42\x4D\x00\x1c"
    message_length = 32
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
    def _validate(cls, message: bytes, header: bytes, length: int) -> BaseMessage:

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

    message_header = b"\x42\x4D\x00\x14"
    message_length = 24
    data_records = slice(6)


class SDS01x(BaseMessage):
    """NovaFitness SDS01x messages"""

    message_header = b"\xAA\xC0"
    message_length = 10
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
    def _validate(cls, message: bytes, header: bytes, length: int) -> BaseMessage:

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
        if sum(msg.payload) == 0:
            raise SensorWarmingUp(f"message empty: warming up sensor")
        return msg

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f"<{len(message)//2}H", message)
