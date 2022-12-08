"""
Read PM sensors

NOTE:
- Sensors are read on passive mode.
- Tested on PMS3003, PMS7003, PMSA003, SDS011 and MCU680
"""
from __future__ import annotations

import sys
import time
from abc import abstractmethod
from contextlib import contextmanager
from csv import DictReader
from pathlib import Path
from textwrap import wrap
from typing import Iterator, NamedTuple

from loguru import logger
from serial import Serial
from typer import progressbar

from pms import SensorNotReady, SensorWarning
from pms.core import Sensor, Supported
from pms.core.types import ObsData

"""translation table for raw.hexdump(n)"""
HEXDUMP_TABLE = bytes.maketrans(
    bytes(range(0x20)) + bytes(range(0x7E, 0x100)), b"." * (0x20 + 0x100 - 0x7E)
)


class UnableToRead(Exception):
    pass


class RawData(NamedTuple):
    """raw messages with timestamp"""

    time: int
    data: bytes

    @property
    def hex(self) -> str:
        return self.data.hex()

    def hexdump(self, line: int | None = None) -> str:
        offset = time if line is None else line * len(self.data)
        hex = " ".join(wrap(self.data.hex(), 2))  # raw.hex(" ") in python3.8+
        dump = self.data.translate(HEXDUMP_TABLE).decode()
        return f"{offset:08x}: {hex}  {dump}"


class Reader:
    @abstractmethod
    def __call__(self, *, raw: bool | None = None) -> Iterator[RawData | ObsData]:
        """
        Return an iterator of ObsData.

        If "raw" is set to True, then ObsData is replaced with RawData.
        """
        ...

    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        self.close()


class SensorReader(Reader):
    """Read sensor messages from serial port

    The sensor is woken up after opening the serial port, and put to sleep when before closing the port.
    While the serial port is open, the sensor is read in passive mode.

    PMS3003 sensors do not accept serial commands, such as wake/sleep or passive mode read.
    Valid messages are extracted from the serial buffer.
    """

    def __init__(
        self,
        sensor: Sensor | Supported | str = Supported.default,
        port: str = "/dev/ttyUSB0",
        interval: int | None = None,
        samples: int | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        """Configure serial port"""
        self.sensor = sensor if isinstance(sensor, Sensor) else Sensor[sensor]
        self.pre_heat = self.sensor.pre_heat
        self.serial = Serial()
        self.serial.port = port
        self.serial.baudrate = self.sensor.baud
        self.serial.timeout = timeout or 5  # max time to wake up sensor
        self.max_retries = max_retries
        self.interval = interval
        self.samples = samples
        logger.debug(
            f"capture {samples if samples else '?'} {sensor} obs "
            f"from {port} every {interval if interval else '?'} secs"
        )

    def _cmd(self, command: str) -> bytes:
        """Write command to sensor and return answer"""

        # send command
        cmd = self.sensor.command(command)
        if cmd.command:
            self.serial.write(cmd.command)
            self.serial.flush()
        elif command.endswith("read"):  # pragma: no cover
            self.serial.reset_input_buffer()

        # return full buffer
        return self.serial.read(max(cmd.answer_length, self.serial.in_waiting))

    def _pre_heat(self):
        if not self.pre_heat:
            return

        logger.info(f"pre-heating {self.sensor} sensor {self.pre_heat} sec")
        with progressbar(range(self.pre_heat), label="pre-heating") as progress:
            for _ in progress:
                time.sleep(1)

        # only pre-heat the firs time
        self.pre_heat = 0

    def open(self) -> None:
        """Open serial port and sensor setup"""
        if not self.serial.is_open:
            logger.debug(f"open {self.serial.port}")
            self.serial.open()
            self.serial.reset_input_buffer()

        # wake sensor and set passive mode
        logger.debug(f"wake {self.sensor}")
        buffer = self._cmd("wake")
        self._pre_heat()
        buffer += self._cmd("passive_mode")
        logger.debug(f"buffer length: {len(buffer)}")

        # check if the sensor answered
        if len(buffer) == 0:
            logger.error(f"Sensor did not respond, check UART pin connections")
            raise UnableToRead("Sensor did not respond")

        # check against sensor type derived from buffer
        if not self.sensor.check(buffer, "passive_mode"):
            logger.error(f"Sensor is not {self.sensor.name}")
            raise UnableToRead("Sensor failed validation")

    def close(self) -> None:
        """Put sensor to sleep and close serial port"""
        logger.debug(f"sleep {self.sensor}")
        buffer = self._cmd("sleep")
        logger.debug(f"close {self.serial.port}")
        self.serial.close()

    def __call__(self, *, raw: bool | None = None) -> Iterator[RawData | ObsData]:
        """Passive mode reading at regular intervals"""

        sample = 0
        failures = 0
        while self.serial.is_open:
            try:
                buffer = self._cmd("passive_read")

                try:
                    obs = self.sensor.decode(buffer)
                except SensorNotReady as e:
                    failures += 1
                    if self.max_retries is not None and failures > self.max_retries:
                        raise
                    logger.debug(e)
                    time.sleep(5)
                except SensorWarning as e:
                    failures += 1
                    if self.max_retries is not None and failures > self.max_retries:
                        raise
                    logger.debug(e)
                    self.serial.reset_input_buffer()
                else:
                    yield RawData(obs.time, buffer) if raw else obs
                    sample += 1
                    if self.samples is not None and sample >= self.samples:
                        break
                    if self.interval:
                        delay = self.interval - (time.time() - obs.time)
                        if delay > 0:
                            time.sleep(delay)
            except KeyboardInterrupt:  # pragma: no cover
                print()
                break


class MessageReader(Reader):
    def __init__(self, path: Path, sensor: Sensor, samples: int | None = None) -> None:
        self.path = path
        self.sensor = sensor
        self.samples = samples

    def open(self) -> None:
        logger.debug(f"open {self.path}")
        self.csv = self.path.open()
        reader = DictReader(self.csv)
        self.data = (row for row in reader if row["sensor"] == self.sensor.name)

    def close(self) -> None:
        logger.debug(f"close {self.path}")
        self.csv.close()

    def __call__(self, *, raw: bool | None = None) -> Iterator[RawData | ObsData]:
        if not hasattr(self, "data"):
            return

        for row in self.data:
            time, message = int(row["time"]), bytes.fromhex(row["hex"])
            yield RawData(time, message) if raw else self.sensor.decode(message, time=time)
            if self.samples:
                self.samples -= 1
                if self.samples <= 0:
                    break


@contextmanager
def exit_on_fail(reader: Reader):
    try:
        with reader:
            yield reader
    except UnableToRead:
        sys.exit(1)
