"""
Read PM sensors

NOTE:
- Sensors are read on passive mode.
- Tested on PMS3003, PMS7003, PMSA003, SDS011 and MCU680
"""

import sys
import time
from csv import DictReader
from pathlib import Path
from textwrap import wrap
from typing import Generator, NamedTuple, Optional, Union, overload

from serial import Serial
from typer import progressbar

from pms import InconsistentObservation, SensorWarmingUp, SensorWarning, logger
from pms.core import Sensor, Supported

from .types import ObsData

"""translation table for raw.hexdump(n)"""
HEXDUMP_TABLE = bytes.maketrans(
    bytes(range(0x20)) + bytes(range(0x7E, 0x100)), b"." * (0x20 + 0x100 - 0x7E)
)


class RawData(NamedTuple):
    """raw messages with timestamp"""

    time: int
    data: bytes

    @property
    def hex(self) -> str:
        return self.data.hex()

    def hexdump(self, line: Optional[int] = None) -> str:
        offset = time if line is None else line * len(self.data)
        hex = " ".join(wrap(self.data.hex(), 2))  # raw.hex(" ") in python3.8+
        dump = self.data.translate(HEXDUMP_TABLE).decode()
        return f"{offset:08x}: {hex}  {dump}"


class SensorReader:
    """Read sensor messages from serial port

    The sensor is woken up after opening the serial port, and put to sleep when before closing the port.
    While the serial port is open, the sensor is read in passive mode.

    PMS3003 sensors do not accept serial commands, such as wake/sleep or passive mode read.
    Valid messages are extracted from the serial buffer.
    """

    def __init__(
        self,
        sensor: Union[Sensor, Supported, str] = Supported.default,
        port: str = "/dev/ttyUSB0",
        interval: Optional[int] = None,
        samples: Optional[int] = None,
    ) -> None:
        """Configure serial port"""
        self.sensor = sensor if isinstance(sensor, Sensor) else Sensor[sensor]
        self.pre_heat = self.sensor.pre_heat
        self.serial = Serial()
        self.serial.port = port
        self.serial.baudrate = self.sensor.baud
        self.serial.timeout = 5  # max time to wake up sensor
        self.interval = interval
        self.samples = samples
        logger.debug(
            f"capture {samples if samples else '?'} {sensor} obs "
            f"from {port} every {interval if interval else '?'} secs"
        )

    def _cmd(self, command: str) -> bytes:  # pragma: no cover
        """Write command to sensor and return answer"""

        # send command
        cmd = self.sensor.command(command)
        if cmd.command:
            self.serial.write(cmd.command)
            self.serial.flush()
        elif command.endswith("read"):
            self.serial.reset_input_buffer()

        # return full buffer
        return self.serial.read(max(cmd.answer_length, self.serial.in_waiting))

    def _pre_heat(self):  # pragma: no cover
        if not self.pre_heat:
            return

        logger.info(f"pre-heating {self.sensor} sensor {self.pre_heat} sec")
        with progressbar(range(self.pre_heat), label="pre-heating") as progress:
            for _ in progress:
                time.sleep(1)

        # only pre-heat the firs time
        self.pre_heat = 0

    def __enter__(self) -> "SensorReader":
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
        if len(buffer) == 0:  # pragma: no cover
            logger.error(f"Sensor did not respond, check UART pin connections")
            sys.exit(1)

        # check against sensor type derived from buffer
        if not self.sensor.check(buffer, "passive_mode"):  # pragma: no cover
            logger.error(f"Sensor is not {self.sensor.name}")
            sys.exit(1)

        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        """Put sensor to sleep and close serial port"""
        logger.debug(f"sleep {self.sensor}")
        buffer = self._cmd("sleep")
        logger.debug(f"close {self.serial.port}")
        self.serial.close()

    @overload
    def __call__(self) -> Generator[ObsData, None, None]:
        ...

    @overload
    def __call__(self, *, raw: bool) -> Generator[RawData, None, None]:
        ...

    def __call__(self, *, raw: Optional[bool] = None):
        """Passive mode reading at regular intervals"""

        sample = 0
        while self.serial.is_open:
            try:
                buffer = self._cmd("passive_read")

                try:
                    obs = self.sensor.decode(buffer)
                except (SensorWarmingUp, InconsistentObservation) as e:  # pragma: no cover
                    logger.debug(e)
                    time.sleep(5)
                except SensorWarning as e:  # pragma: no cover
                    logger.debug(e)
                    self.serial.reset_input_buffer()
                else:
                    yield RawData(obs.time, buffer) if raw else obs
                    sample += 1
                    if self.samples is not None and sample >= self.samples:
                        break
                    if self.interval:  # pragma: no cover
                        delay = self.interval - (time.time() - obs.time)
                        if delay > 0:
                            time.sleep(delay)
            except KeyboardInterrupt:  # pragma: no cover
                print()
                break


class MessageReader:
    def __init__(self, path: Path, sensor: Sensor, samples: Optional[int] = None) -> None:
        self.path = path
        self.sensor = sensor
        self.samples = samples

    def __enter__(self) -> "MessageReader":
        logger.debug(f"open {self.path}")
        self.csv = self.path.open()
        reader = DictReader(self.csv)
        self.data = (row for row in reader if row["sensor"] == self.sensor.name)
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        logger.debug(f"close {self.path}")
        self.csv.close()

    @overload
    def __call__(self) -> Generator[ObsData, None, None]:
        ...

    @overload
    def __call__(self, *, raw: bool) -> Generator[RawData, None, None]:
        ...

    def __call__(self, *, raw: Optional[bool] = None):
        for row in self.data:
            time, message = int(row["time"]), bytes.fromhex(row["hex"])
            yield RawData(time, message) if raw else self.sensor.decode(message, time=time)
            if self.samples:  # pragma: no cover
                self.samples -= 1
                if self.samples <= 0:
                    break
