"""
Read a PMS5003/PMS7003/PMSA003 sensor

NOTE:
- Sensor are read on passive mode.
- Active mode (sleep/wake) is not supported.
- Should work on a PMS1003 sensor, but has not been tested.
- Should work on a PMS3003 sensor, but has not been tested.
"""

import struct, logging, os
from datetime import datetime
from typing import NamedTuple, Optional, Tuple, Generator
from serial import Serial

logging.basicConfig(level=os.environ.get("LEVEL", "WARNING"))
logger = logging.getLogger(__name__)


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

        logger.debug(f"buffer={buffer}")
        try:
            header = buffer[:4]
            msg_len = {
                b"\x42\x4D\x00\x1c": 32,  # PMS1003, PMS5003, PMS7003, PMSA003
                b"\x42\x4D\x00\x14": 24,  # PMS3003
            }[header]
        except KeyError as e:
            raise UserWarning(f"message header: {header}") from e

        if len(buffer) != msg_len:
            raise UserWarning(f"message length: {len(buffer)}")

        msg = struct.unpack(f">{(msg_len//2)}H", buffer)
        checksum = sum(buffer[:-2])
        if msg[-1] != checksum:
            raise UserWarning(f"message checksum {msg[-1]:#x} != {checksum:#x}")

        if msg_len == 32:
            return cls(time, *msg[5:14])
        else:
            return cls(time, *msg[5:8])


def read(port: str = "/dev/ttyUSB0") -> Generator[SensorData, None, None]:
    """Read PMSx003 messages from serial port
    
    Passive mode reading. Active mode (sleep/wake) is not supported.
    """
    with Serial(port, timeout=0) as ser:  # 9600 8N1 by default
        ser.write(b"\x42\x4D\xE1\x00\x00\x01\x70")  # set passive mode
        ser.flush()
        ser.reset_input_buffer()
        while ser.in_waiting < 8:
            continue
        if ser.read(8) == b"\x42\x4D\x00\x04\xe1\x00\x01\x74":
            logger.debug(f"Assume PMS1003|PMS5003|PMS7003|PMSA003")
            msg_len = 32
        else:
            logger.debug(f"Assume PMS3003")
            msg_len = 24
        logger.debug(f"Inferred message length {msg_len}")

        while ser.is_open:
            ser.write(b"\x42\x4D\xE2\x00\x00\x01\x71")  # passive mode read
            ser.flush()
            while ser.in_waiting < msg_len:
                continue
            try:
                yield SensorData.decode(ser.read(msg_len))
            except UserWarning as e:
                ser.reset_input_buffer()
                logger.debug(e)
