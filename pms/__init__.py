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
from enum import Enum
from typing import NamedTuple, Optional, Tuple, Callable, Generator
from serial import Serial

logging.basicConfig(level=os.environ.get("LEVEL", "WARNING"))
logger = logging.getLogger(__name__)


class SensorWarning(UserWarning):
    """Recoverable errors"""

    pass


class WrongMessageFormat(SensorWarning):
    """Wrongly formattted message: throw away observation"""

    pass


class WrongMessageChecksum(SensorWarning):
    """Failed message checksum: throw away observation"""

    pass


class SensorWarmingUp(SensorWarning):
    """Empty message: throw away observation and wait until sensor warms up"""

    pass


class SensorMessage(NamedTuple):
    header: bytes
    payload: bytes
    checksum: bytes

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> "SensorMessage":
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
    def decode(cls, message: bytes, header: bytes, length: int) -> "SensorMessage":
        try:
            # validate full message
            return cls._validate(message, header, length)
        except WrongMessageFormat as e:
            # search last complete message on buffer
            start = message.rfind(header, 0, 4 - length)
            if start < 0:  # No match found
                raise
            # validate last complete message
            return cls._validate(message[start : start + length], header, length)

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f">{len(message)//2}H", message)

    @property
    def data(self) -> Tuple[int, ...]:
        return self._unpack(self.payload)


class SensorData(NamedTuple):
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

    def timestamp(self, fmt: str = "%F %T") -> str:
        """measurement time as formatted string"""
        return datetime.fromtimestamp(self.time).strftime(fmt)

    @property
    def cf01(self) -> float:
        return self.pm01 / self.raw01 if self.raw01 else 0

    @property
    def cf25(self) -> float:
        return self.pm25 / self.raw25 if self.raw25 else 0

    @property
    def cf10(self) -> float:
        return self.pm10 / self.raw10 if self.raw10 else 0

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = spec[:-2] + "d"
            f = f"{self.timestamp()}: PM1 {{:{d}}}, PM2.5 {{:{d}}}, PM10 {{:{d}}} ug/m3"
            return f.format(self.pm01, self.pm25, self.pm10)
        if spec.endswith("csv"):
            d = spec[:-3] + "d"
            f = f"{self.time}, {{1}}, {{2}}, {{3}}, {{4}}, {{5}}, {{6}}, {{7}}, {{8}}, {{9}}, {{10}}, {{11}}, {{12}}"
        elif spec.endswith("num"):
            d = spec[:-3] + "d"
            f = f"{self.timestamp()}: N0.3 {{7}}, N0.5 {{8}}, N1.0 {{9}}, N2.5 {{10}}, N5.0 {{11}}, N10 {{12}} #/100cc"
        elif spec.endswith("cf"):
            d = (spec[:-2] or ".1") + "f"
            f = f"{self.timestamp()}: CF1 {{:{d}}}, CF2.5 {{:{d}}}, CF10 {{:{d}}}"
            return f.format(self.cf01, self.cf25, self.cf10)
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


class SensorType(Enum):
    """Supported PM sensors
    
    message signature: header, length
    - PMS3003 messages are 24b long;
    - All other PMSx003 messages are 32b long.
    """

    PMSx003 = (b"\x42\x4D\x00\x1c", 32)
    PMS1003 = PMS5003 = PMS7003 = PMSA003 = PMSx003
    PMS3003 = (b"\x42\x4D\x00\x14", 24)
    Default = (b"", 0)

    @property
    def header(self) -> bytes:
        return self.value[0]

    @property
    def length(self) -> int:
        return self.value[1]

    @property
    def has_number_concentration(self) -> bool:
        return self == self.__class__.PMSx003

    @property
    def accept_commands(self) -> bool:
        return self != self.__class__.PMS3003

    def decode(self, buffer: bytes, *, time: Optional[int] = None) -> SensorData:
        """Decode a PMSx003/PMS3003 message"""
        if not time:
            time = SensorData.now()

        data = SensorMessage.decode(buffer, self.header, self.length).data
        logger.debug(f"message data: {data}")

        if self.has_number_concentration:
            records = 12  # 3 cf, 3 pm, 6 num
        else:
            records = 6  # 3 cf and 3 pm

        return SensorData(time, *data[:records])


class PMSerial:
    """Read PMSx003 messages from serial port
    
    The sensor is woken up after opening the serial port,
    and put to sleep when before closing the port.
    While the serial port is open, the sensor is read in passive mode.

    PMS3003 sensors do not accept serial commands, such as wake/sleep
    or passive mode read. Valid messages are extracted from the serail buffer.
    Support for this sensor is experimental.
    """

    def __init__(self, port: str = "/dev/ttyUSB0") -> None:
        """Configure serial port"""
        self.serial = Serial()
        self.serial.port = port
        self.serial.timeout = 0
        self.sensor = SensorType.Default  # updated later

    def _cmd(self, command: str) -> bytes:
        """PMSx003 serial commands (except PMS3003)"""

        # send command
        if self.sensor.accept_commands:
            cmd = dict(
                passive_mode=b"\x42\x4D\xE1\x00\x00\x01\x70",
                passive_read=b"\x42\x4D\xE2\x00\x00\x01\x71",
                active_mode=b"\x42\x4D\xE1\x00\x01\x01\x71",
                sleep=b"\x42\x4D\xE4\x00\x00\x01\x73",
                wake=b"\x42\x4D\xE4\x00\x01\x01\x74",
            )[command]
            self.serial.write(cmd)
            self.serial.flush()
        elif command.endswith("read"):
            self.serial.reset_input_buffer()

        # wait for answer
        length = self.sensor.length if command.endswith("read") else 8
        while self.serial.in_waiting < length:
            continue

        # return full buffer
        return self.serial.read(self.serial.in_waiting)

    def __enter__(self) -> Callable[[int], Generator[SensorData, None, None]]:
        """Open serial port and sensor setup"""
        if not self.serial.is_open:
            self.serial.open()

        # wake sensor
        self.serial.reset_input_buffer()
        buffer = self._cmd("wake")

        # set passive mode
        buffer += self._cmd("passive_mode")

        # guess sensor type from answer
        if buffer[-8:] == b"\x42\x4D\x00\x04\xe1\x00\x01\x74":
            self.sensor = SensorType.PMSx003
        else:
            self.sensor = SensorType.PMS3003
        logger.debug(f"Assume {self.sensor.name}, #{self.sensor.length}b message")

        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        """Put sensor to sleep and close serial port"""
        buffer = self._cmd("sleep")
        self.serial.close()

    def __call__(self, interval: int = 0) -> Generator[SensorData, None, None]:
        """Passive mode reading at regular intervals"""
        while self.serial.is_open:
            # passive mode read
            buffer = self._cmd("passive_read")

            try:
                obs = self.sensor.decode(buffer)
            except SensorWarmingUp as e:
                logger.debug(e)
                time.sleep(1)
            except SensorWarning as e:
                logger.debug(e)
                self.serial.reset_input_buffer()
            else:
                yield obs
                delay = interval - (time.time() - obs.time)
                if delay > 0:
                    time.sleep(delay)
