#!/usr/bin/env python3

"""
Read a PMS5003/PMS7003/PMSA003 sensor
"""

import time, struct
from dataclasses import dataclass
from typing import List, Union, Generator
from serial import Serial


@dataclass
class Obs:
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
    # seconds since epoch
    time: int = int(time.time())

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


def decode(buffer: List[int]) -> Obs:
    # print(buffer)
    assert len(buffer) == 32, f"message len={len(buffer)}"

    msg_len = len(buffer) // 2
    msg = struct.unpack(f">{'H'*msg_len}", bytes(buffer))
    assert msg[0] == 0x424D, f"message header={msg[0]:#x}"
    assert msg[1] == 28, f"body length={msg[1]}"

    checksum = sum(buffer[:-2])
    assert msg[-1] == checksum, f"checksum {msg[-1]:#x} != {checksum:#x}"

    return Obs(*msg[5:14])


def read(device: str = "/dev/ttyUSB0") -> Generator[Obs, None, None]:
    dev = Serial(device, 9600)  # , timeout=0)
    if not dev.is_open():
        dev.open()
    dev.write(b"\x42\x4D\xE1\x00\x00\x01\x70")  # set passive mode
    dev.flush()
    dev.reset_input_buffer()

    while dev.is_open():
        dev.write(b"\x42\x4D\xE2\x00\x00\x01\x71")  # passive mode read
        dev.flush()
        while dev.in_waiting < 32:
            continue

        try:
            yield decode(dev.read(32))
        except AssertionError as e:
            dev.reset_input_buffer()
            print(e)


def main(read_delay: Union[int, str] = 60, **kwargs) -> None:
    for pm in read(**kwargs):
        print(f"{pm}")

        delay = int(read_delay) - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)


if __name__ == "__main__":
    import sys

    try:
        main(*sys.argv[1:])
    except KeyboardInterrupt:
        print()
