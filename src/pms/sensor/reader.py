"""
Read PM sensors

NOTE:
- Sensors are read on passive mode.
- Tested on PMS3003, PMS7003, PMSA003, SDS011 and MCU680
"""

import sys
import time
from typing import Generator, Optional

from serial import Serial

from pms import logger, SensorWarning, SensorWarmingUp, InconsistentObservation
from pms.sensor import Sensor, base


class SensorReader:
    """Read sensor messages from serial port

    The sensor is woken up after opening the serial port, and put to sleep when before closing the port.
    While the serial port is open, the sensor is read in passive mode.

    PMS3003 sensors do not accept serial commands, such as wake/sleep or passive mode read.
    Valid messages are extracted from the serail buffer. Support for this sensor is experimental.
    """

    def __init__(
        self,
        sensor: str = "PMSx003",
        port: str = "/dev/ttyUSB0",
        interval: Optional[int] = None,
        samples: Optional[int] = None,
    ) -> None:
        """Configure serial port"""
        self.sensor = Sensor[sensor]
        self.serial = Serial()
        self.serial.port = port
        self.serial.baudrate = self.sensor.baud
        self.serial.timeout = 5  # max time to wake up sensor
        self.interval = interval
        self.samples = samples
        logger.debug(
            f"Reader: "
            f"request {samples if samples else '?'} obs "
            f"from {sensor} on {port} "
            f"every {interval if interval else '?'} secs"
        )

    def _cmd(self, command: str) -> bytes:
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

    def __enter__(self) -> "SensorReader":
        """Open serial port and sensor setup"""
        if not self.serial.is_open:
            self.serial.open()
            self.serial.reset_input_buffer()

        # wake sensor and set passive mode
        buffer = self._cmd("wake") + self._cmd("passive_mode")
        logger.debug(f"buffer length: {len(buffer)}")

        # check against sensor type derived from buffer
        if not self.sensor.check(buffer, "passive_mode"):
            logger.error(f"Sensor is not {self.sensor.name}")
            sys.exit(1)

        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        """Put sensor to sleep and close serial port"""
        buffer = self._cmd("sleep")
        self.serial.close()

    def __call__(self) -> Generator[base.ObsData, None, None]:
        """Passive mode reading at regular intervals"""
        while self.serial.is_open:
            try:
                buffer = self._cmd("passive_read")

                try:
                    obs = self.sensor.decode(buffer)
                except (SensorWarmingUp, InconsistentObservation) as e:
                    logger.debug(e)
                    time.sleep(5)
                except SensorWarning as e:
                    logger.debug(e)
                    self.serial.reset_input_buffer()
                else:
                    yield obs
                    if self.samples:
                        self.samples -= 1
                        if self.samples <= 0:
                            break
                    if self.interval:
                        delay = self.interval - (time.time() - obs.time)
                        if delay > 0:
                            time.sleep(delay)
            except KeyboardInterrupt:
                print()
                break
