"""
NovaFitness SDS01x PM2.5/PM10 sensors

The SDS198 PM100 sensor is not supported
"""

import struct
from datetime import datetime
from typing import NamedTuple, Optional, Tuple
from pms import logger, WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp


class Message(NamedTuple):
    header: bytes
    payload: bytes
    checksum: int
    tail: int

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> "Message":
        # consistency check: bug in message singnature
        assert len(header) == 2, f"wrong header length {len(header)}"
        assert header[:1] == b"\xAA", f"wrong header start {header}"
        assert length == 10, f"wrong payload length {length}"

        # validate message: recoverable errors (throw away observation)
        logger.debug(f"message hex: {message.hex()}")
        msg = cls(message[:2], message[2:-2], message[-2], message[-1])
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

    @classmethod
    def decode(cls, message: bytes, header: bytes, length: int) -> Tuple[int, ...]:
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
        logger.debug(f"message payload: {msg.payload.hex()}")
        return cls._unpack(msg.payload)

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f"<{len(message)//2}H", message)


class Data(NamedTuple):
    """SDS01x observations
    
    time                                    measurement time [seconds since epoch]
    pm25, pm10                              PM2.5, PM10 [ug/m3]
    """

    # seconds since epoch
    time: int
    # rawX [0.1 ug/m3]: PM2.5*10 & PM10*10
    raw25: int
    raw10: int

    @property
    def pm25(self) -> float:
        """extract PM2.5 (float) from raw25 (int)"""
        return self.raw25 / 10

    @property
    def pm10(self) -> float:
        """extract PM10 (float) from raw25 (int)"""
        return self.raw10 / 10

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = (spec[:-2] or ".1") + "f"
            return f"{self.date:%F %T}: PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = (spec[:-3] or ".1") + "f"
            return f"{self.time}, {self.pm25:{d}}, {self.pm10:{d}}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")

    @staticmethod
    def now() -> int:
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())
