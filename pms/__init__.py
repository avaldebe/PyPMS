"""
Read a PMS5003/PMS7003/PMSA003 sensor

NOTE:
- Should work on a PMS1003 sensor, but has not been tested.
- PMS3003 sensor is not supported.
- Sensor are read on passive mode.
- Active mode (sleep/wake) is not supported.
"""

import struct, logging, os
from datetime import datetime
from typing import NamedTuple, List, Generator
from serial import Serial

logging.basicConfig(level=os.environ.get("LEVEL", "WARNING"))
logger = logging.getLogger(__name__)


class Obs(NamedTuple):
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
    n0_3: int
    n0_5: int
    n1_0: int
    n2_5: int
    n5_0: int
    n10_0: int

    @staticmethod
    def now() -> int:
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())

    @staticmethod
    def to_datetime(time: int) -> datetime:
        """seconds since epoch to datetime"""
        return datetime.fromtimestamp(time)

    def timestamp(self, fmt: str = "%F %T"):
        """measurement time as formatted string"""
        return self.to_datetime(self.time).strftime(fmt)

    def __format__(self, spec: str) -> str:
        if spec:
            d = f"{spec[:-1]}d"
        if spec.endswith("s"):
            return f"{self.timestamp()}: PM1 {self.pm01:{d}}, PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("c"):
            return (
                f"{self.time}, "
                f"{self.pm01:{d}}, {self.pm25:{d}}, {self.pm10:{d}}, "
                f"{self.n0_3:{d}}, {self.n0_5:{d}}, {self.n1_0:{d}}, "
                f"{self.n2_5:{d}}, {self.n5_0:{d}}, {self.n10_0:{d}}"
            )
        if spec.endswith("m"):
            return f"PM1 {self.pm01:{d}}, PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("n"):
            return (
                f"N0.3 {self.n0_3:{d}}, N0.5 {self.n0_5:{d}}, N1.0 {self.n1_0:{d}}, "
                f"N2.5 {self.n2_5:{d}}, N5.0 {self.n5_0:{d}}, N10 {self.n10_0:{d}} #/100cc"
            )
        raise ValueError(
            f"Unknown format code '{spec}' for object of type '{__name__}.Obs'"
        )

    def __str__(self):
        return self.__format__("s")


def decode(time: int, buffer: List[int]) -> Obs:
    """Decode a PMSx003 message (32b long)
    
    PMS3003 messages are 24b long. PMS3003 is not supported.
    """
    logger.debug(buffer)
    if len(buffer) != 32:
        raise UserWarning(f"message total length: {len(buffer)}")

    msg_len = len(buffer) // 2
    msg = struct.unpack(f">{'H'*msg_len}", bytes(buffer))
    if msg[0] != 0x424D:
        raise UserWarning(f"message start header: {msg[0]:#x}")
    if msg[1] != 28:
        raise UserWarning(f"message body length: {msg[1]}")

    checksum = sum(buffer[:-2])
    if msg[-1] != checksum:
        raise UserWarning(f"message checksum {msg[-1]:#x} != {checksum:#x}")

    return Obs(time, *msg[5:14])


def read(port: str = "/dev/ttyUSB0") -> Generator[Obs, None, None]:
    """Read PMSx003 messages from serial port
    
    Passive mode reading. Active mode (sleep/wake) is not supported.
    """
    with Serial(port, timeout=0) as ser:  # 9600 8N1 by default
        ser.write(b"\x42\x4D\xE1\x00\x00\x01\x70")  # set passive mode
        ser.flush()
        ser.reset_input_buffer()

        while ser.is_open:
            ser.write(b"\x42\x4D\xE2\x00\x00\x01\x71")  # passive mode read
            ser.flush()
            while ser.in_waiting < 32:
                continue
            try:
                logger.debug(f"serail buffer #{ser.in_waiting}")
                yield decode(Obs.now(), ser.read(32))
            except UserWarning as e:
                ser.reset_input_buffer()
                logger.debug(e)
