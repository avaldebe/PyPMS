"""
Plantower PMSx003 sensors
"""

import struct
from datetime import datetime
from enum import Enum
from typing import NamedTuple, Optional, Tuple
from .logging import logger, WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp


class Message(NamedTuple):
    header: bytes
    payload: bytes
    checksum: bytes

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> "Message":
        # consistency check: bug in message singnature
        assert len(header) == 4, f"wrong header length {len(header)}"
        assert header[:2] == b"BM", f"wrong header start {header}"
        len_payload, = cls._unpack(header[-2:])
        assert length == len(header) + len_payload, f"wrong payload length {length}"

        # validate message: recoverable errors (throw away observation)
        logger.debug(f"message hex: {message.hex()}")
        msg = cls(message[:4], message[4:-2], message[-2:])
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)}")
        checksum, = cls._unpack(msg.checksum)
        checksum_ = sum(msg.header) + sum(msg.payload)
        if checksum != checksum_:
            raise WrongMessageChecksum(f"message checksum {checksum} != {checksum_}")
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
        return cls._unpack(msg.payload)

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f">{len(message)//2}H", message)


class Data(NamedTuple):
    """PMSx003 observations
    
    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [ug/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [ug/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations under X.Y um [#/100cc]
    """

    # seconds since epoch
    time: int
    # rawX [ug/m3]: raw (cf=1) PM1.0, PM2.5 & PM10 estimate
    raw01: int
    raw25: int
    raw10: int
    # pmX [ug/m3]: PM1.0, PM2.5 & PM10
    pm01: int
    pm25: int
    pm10: int
    # nX_Y [#/100cc]: number concentrations under X.Y um
    n0_3: Optional[int] = None
    n0_5: Optional[int] = None
    n1_0: Optional[int] = None
    n2_5: Optional[int] = None
    n5_0: Optional[int] = None
    n10_0: Optional[int] = None

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    @staticmethod
    def _safe_div(x: int, y: int) -> float:
        if y:
            return x / y
        if x == y == 0:
            return 1
        return 0

    @property
    def cf01(self) -> float:
        return self._safe_div(self.pm01, self.raw01)

    @property
    def cf25(self) -> float:
        return self._safe_div(self.pm25, self.raw25)

    @property
    def cf10(self) -> float:
        return self._safe_div(self.pm10, self.raw10)

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = spec[:-2] + "d"
            return f"{self.date:%F %T}: PM1 {self.pm01:{d}}, PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = spec[:-3] + "d"
            f = f"{self.time}, {{1}}, {{2}}, {{3}}, {{4}}, {{5}}, {{6}}, {{7}}, {{8}}, {{9}}, {{10}}, {{11}}, {{12}}"
        elif spec.endswith("num"):
            d = spec[:-3] + "d"
            f = f"{self.date:%F %T}: N0.3 {{7}}, N0.5 {{8}}, N1.0 {{9}}, N2.5 {{10}}, N5.0 {{11}}, N10 {{12}} #/100cc"
        elif spec.endswith("cf"):
            d = (spec[:-2] or ".0") + "%"
            return f"{self.date:%F %T}: CF1 {self.cf01:{d}}, CF2.5 {self.cf25:{d}}, CF10 {self.cf10:{d}}"
        if d and f:
            return f.format(*(f"{x:{d}}" if x is not None else "" for x in self))
        else:
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


class Sensor(Enum):
    """Supported PM sensors
    
    message signature: header, length
    - PMS3003 messages are 24b long;
    - All other PMSx003 messages are 32b long.
    """

    PMSx003 = (b"\x42\x4D\x00\x1c", 32)
    PMS1003 = PMS5003 = PMS7003 = PMSA003 = PMSx003
    PMS3003 = (b"\x42\x4D\x00\x14", 24)
    Default = PMSx003

    @property
    def message_header(self) -> bytes:
        return self.value[0]

    @property
    def message_length(self) -> int:
        return self.value[1]

    @property
    def message_records(self) -> int:
        """Data records in message"""
        return {"PMS3003": 6, "PMSx003": 12}[self.name]

    def command(self, command: str) -> bytes:
        """Serial commands (except PMS3003)"""
        return {
            "PMS3003": b"",
            "PMSx003": {
                "passive_mode": b"\x42\x4D\xE1\x00\x00\x01\x70",
                "passive_read": b"\x42\x4D\xE2\x00\x00\x01\x71",
                "active_mode": b"\x42\x4D\xE1\x00\x01\x01\x71",
                "sleep": b"\x42\x4D\xE4\x00\x00\x01\x73",
                "wake": b"\x42\x4D\xE4\x00\x01\x01\x74",
            }[command],
        }[self.name]

    def answer_length(self, command: str) -> int:
        """Expected answer length to serial command"""
        return self.message_length if command.endswith("read") else 8

    @classmethod
    def guess(cls, buffer: bytes) -> "Sensor":
        """Guess sensor type from buffer contents"""
        if buffer[-8:] == b"\x42\x4D\x00\x04\xe1\x00\x01\x74":
            sensor = cls.PMSx003
        else:
            sensor = cls.PMS3003
        logger.debug(f"Assume {sensor.name}, #{sensor.message_length}b message")
        return sensor

    def decode(self, buffer: bytes, *, time: Optional[int] = None) -> Data:
        """Decode a PMSx003/PMS3003 message"""
        if not time:
            time = Data.now()

        data = Message.decode(buffer, self.message_header, self.message_length)
        logger.debug(f"message data: {data}")

        return Data(time, *data[: self.message_records])
