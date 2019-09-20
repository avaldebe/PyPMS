"""
Read a PMS5003/PMS7003/PMSA003 sensor

NOTE:
- Sensor are read on passive mode.
- Active mode (sleep/wake) is not supported.
- Should work on a PMS1003 sensor, but has not been tested.
- Should work on a PMS3003 sensor, but has not been tested.
"""

import struct, logging, os, time
from datetime import datetime
from typing import NamedTuple, Optional, Tuple, Callable, Generator
from serial import Serial

logging.basicConfig(level=os.environ.get("LEVEL", "WARNING"))
logger = logging.getLogger(__name__)


class SensorMessage(NamedTuple):
    header: bytes
    payload: bytes
    checksum: int
    length: int

    @classmethod
    def _decode(cls, message: bytes) -> "SensorMessage":
        header, payload, checksum = message[:4], message[4:-2], message[-2:]
        return cls(header, payload, cls._unpack(checksum)[0], len(message))

    @classmethod
    def decode(cls, message: bytes, header: bytes, length: int) -> "SensorMessage":
        if message[:4] == header and len(message) == length:
            return cls._decode(message)

        # search last complete message on buffer
        start = message.rfind(header, 0, 4 - length)
        if start >= 0:  # found complete message
            logger.debug(f"message full: {message.hex()}")
            message = message[start : start + length]  # last complete message
            logger.debug(f"message trim: {message.hex()}")
            return cls._decode(message)

        # No match found
        return cls._decode(message)

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f">{len(message)//2}H", message)

    def _checksum(self) -> int:
        return sum(self.header) + sum(self.payload)

    def __bool__(self) -> bool:
        return self.checksum == self._checksum()

    @property
    def data(self) -> Tuple[int, ...]:
        return self._unpack(self.payload)


class SensorData(NamedTuple):
    """PMSx003 observations
    
    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [ug/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations under X.Y um [#/100cc]
    """

    # seconds since epoch
    time: int
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

    def timestamp(self, fmt: str = "%F %T"):
        """measurement time as formatted string"""
        return datetime.fromtimestamp(self.time).strftime(fmt)

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = spec.replace("pm", "d")
            f = f"{self.timestamp()}: PM1 {{1}}, PM2.5 {{2}}, PM10 {{3}} ug/m3"
        if spec.endswith("csv"):
            d = spec.replace("csv", "d")
            f = f"{self.time}, {{1}}, {{2}}, {{3}}, {{4}}, {{5}}, {{6}}, {{7}}, {{8}}, {{9}}"
        if spec.endswith("num"):
            d = spec.replace("num", "d")
            f = f"{self.timestamp()}: N0.3 {{4}}, N0.5 {{5}}, N1.0 {{6}}, N2.5 {{7}}, N5.0 {{8}}, N10 {{9}} #/100cc"
        if d and f:
            return f.format(*tuple(f"{x:{d}}" if x is not None else "" for x in self))
        else:
            raise ValueError(
                f"Unknown format code '{spec}' for object of type '{__name__}.SensorData'"
            )

    def __str__(self):
        return self.__format__("pm")

    @staticmethod
    def now() -> int:
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())

    @classmethod
    def decode(cls, buffer: bytes, *, time: Optional[int] = None) -> "SensorData":
        """Decode a PMSx003 message (24b or 32b long)
        
        PMS3003 messages are 24b long. All other PMSx003 messages are 32b long
        """
        if not time:
            time = cls.now()

        msg_desc = {  # header: length
            b"\x42\x4D\x00\x1c": 32,  # PMS1003, PMS5003, PMS7003, PMSA003
            b"\x42\x4D\x00\x14": 24,  # PMS3003
        }
        for header, length in msg_desc.items():
            msg = SensorMessage.decode(buffer, header, length)
            if msg:
                break

        try:
            length = msg_desc[msg.header]
        except KeyError as e:
            raise UserWarning(f"message header: {msg.header}")

        if msg.length != length:
            raise UserWarning(f"message length: {msg.length}")

        if not msg:
            raise UserWarning(f"message checksum {msg.checksum} != {msg._checksum()}")

        if msg.length == 32:
            return cls(time, *msg.data[3:12])
        else:
            return cls(time, *msg.data[3:6])


class PMSerial:
    """Read PMSx003 messages from serial port"""

    def __init__(self, port: str = "/dev/ttyUSB0"):
        """Configure serial port"""
        self.serial = Serial()
        self.serial.port = port
        self.serial.timeout = 0

    def __enter__(self) -> Callable[[int], Generator[SensorData, None, None]]:
        """Open serial port"""
        if not self.serial.is_open:
            self.serial.open()
        self.serial.write(b"\x42\x4D\xE1\x00\x00\x01\x70")  # set passive mode
        self.serial.flush()
        self.serial.reset_input_buffer()
        while self.serial.in_waiting < 8:
            continue
        if self.serial.read(8) == b"\x42\x4D\x00\x04\xe1\x00\x01\x74":
            logger.debug(f"Assume PMS1003|PMS5003|PMS7003|PMSA003")
            self.msg_len = 32
        else:
            logger.debug(f"Assume PMS3003")
            self.msg_len = 24
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Close serial port"""
        self.serial.close()

    def __call__(self, interval: int = 0) -> Generator[SensorData, None, None]:
        """Passive mode reading.
        
        Active mode (sleep/wake) is not supported.
        """
        while self.serial.is_open:
            self.serial.write(b"\x42\x4D\xE2\x00\x00\x01\x71")  # passive mode read
            self.serial.flush()
            while self.serial.in_waiting < self.msg_len:
                continue
            buffer = self.serial.read(self.serial.in_waiting)

            try:
                obs = SensorData.decode(buffer)
            except UserWarning as e:
                self.serial.reset_input_buffer()
                logger.debug(e)
            else:
                yield obs
                delay = interval - (time.time() - obs.time)
                if delay > 0:
                    time.sleep(delay)
