#!/usr/bin/env python3

"""
Read a PMS5003/PMS7003/PMSA003 sensor
"""

import time, struct
from dataclasses import dataclass
from typing import List, Tuple, Any, Union
from serial import Serial


@dataclass
class Obs:
    pm01: int
    pm25: int
    pm10: int
    time: int = int(time.time())

    def timestamp(self):
        return time.strftime("%F %T %Z", time.gmtime(self.time))

    def str_pm(self):
        return f"PM1 {self.pm01}, PM2.5 {self.pm25}, PM10 {self.pm10} ug/m3"

    def csv(self):
        return f"{self.time}, {self.pm01}, {self.pm25}, {self.pm10}"

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

    return Obs(*msg[5:8])


def read(device: str = "/dev/ttyUSB0") -> Obs:
    dev = Serial(device, 9600)  # , timeout=0)
    if not dev.isOpen():
        dev.open()
        dev.write(b"\x42\x4D\xE1\x00\x00\x01\x70")  # set passive mode
        dev.flush()
        while dev.in_waiting:
            print(dev.read())

    dev.write(b"\x42\x4D\xE2\x00\x00\x01\x71")  # passive mode read
    dev.flush()
    while dev.in_waiting < 32:
        continue

    return decode(dev.read(32))


def main(read_delay: Union[int, str] = 60, **kwargs) -> None:
    last_msg_time = time.time()
    while True:
        try:
            pm = read(**kwargs)
        except AssertionError as e:
            print(e)
            pass
        else:
            print(f"{pm}")
        finally:
            delay = int(read_delay) - (time.time() - last_msg_time)
            if delay > 0:
                time.sleep(delay)
            last_msg_time = pm.time


if __name__ == "__main__":
    import sys

    try:
        main(*sys.argv[1:])
    except KeyboardInterrupt:
        print()
