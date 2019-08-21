"""
Read a PMS5003/PMS7003/PMSA003 sensor and print the PM measurements

Notes:
- Needs Python 3.7+ for dataclasses
"""

import time, struct, logging, os
from typing import List, Generator, NamedTuple
from serial import Serial, EIGHTBITS, PARITY_NONE, STOPBITS_ONE

logging.basicConfig(level=os.environ.get("LEVEL", "WARNING"))
logger = logging.getLogger(__name__)


class Obs(NamedTuple):
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

    def timestamp(self):
        return time.strftime("%F %T %Z", time.gmtime(self.time))

    def str_pm(self):
        return f"PM1 {self.pm01}, PM2.5 {self.pm25}, PM10 {self.pm10} ug/m3"

    def str_nc(self):
        return f"N0.3 {self.n0_3}, N0.5 {self.n0_5}, N1.0 {self.n1_0}, N2.5 {self.n2_5}, N5.0 {self.n5_0}, N10 {self.n10_0} #/100cc"

    def csv(self):
        return f"{self.time}, {self.pm01}, {self.pm25}, {self.pm10}, {self.n0_3}, {self.n0_5}, {self.n1_0}, {self.n2_5}, {self.n5_0}, {self.n10_0}"

    def __str__(self):
        return f"{self.timestamp()}: {self.str_pm()}"


def decode(time: int, buffer: List[int]) -> Obs:
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
    with Serial(  # 9600 8N1, 1.5s timeout
        port or "/dev/ttyUSB0",
        baudrate=9600,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
        timeout=0,
    ) as ser:
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
                yield decode(int(time.time()), ser.read(32))
            except UserWarning as e:
                ser.reset_input_buffer()
                logger.debug(e)


def main(interval: int, serial: str, csv: bool) -> None:
    for pm in read(serial):
        if csv:
            print(pm.csv())
        else:
            print(pm)

        delay = int(interval) - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)
