#!/usr/bin/env python3

"""
Read a PMS5003/PMS7003/PMSA003 sensor
"""

import time, struct
from collections import namedtuple
from serial import Serial

PMS = namedtuple("PMS", "time pm01 pm25 pm10", module="PyPMS")
PMS.str_time = lambda self: time.strftime("%F %T %Z", time.gmtime(self.time))
PMS.str_pm = lambda self: f"PM1 {self.pm01}, PM2.5 {self.pm25}, PM10 {self.pm10} ug/m3"
PMS.__str__ = lambda self: f"{self.str_time()}: {self.str_pm()}"


def read_pms(device: str = "/dev/ttyUSB0") -> PMS:
    dev = Serial(device, 9600)  # , timeout=0)
    if not dev.isOpen():
        dev.open()
        dev.write(b"\x42\x4D\xE1\x00\x00\x01\x70")  # set passive mode
        dev.flush()
        while dev.in_waiting:
            print(dev.read())

    while dev.isOpen():
        dev.write(b"\x42\x4D\xE2\x00\x00\x01\x71")  # passive mode read
        dev.flush()
        while dev.in_waiting < 32:
            continue

        buffer = dev.read(32)
        # print(buffer)
        assert len(buffer) == 32, f"message len={len(buffer)}"
        msg = struct.unpack(">HHHHHHHHHHHHHHHH", bytes(buffer))
        assert msg[0] == 0x424D, f"message header={msg[0]:#x}"
        assert msg[1] == 28, f"body length={msg[1]}"
        cksum = sum(buffer[:-2])
        assert msg[-1] == cksum, f"checksum {msg[-1]:#x} != {cksum:#x}"
        return PMS(time.time(), *msg[5:8])


def main(read_delay: int = 60, device: str = "/dev/ttyUSB0") -> None:
    last_msg_time = time.time()
    while True:
        try:
            pm = read_pms(device)
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
