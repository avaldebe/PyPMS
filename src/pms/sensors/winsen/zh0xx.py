"""
Winsen ZH03B/ZH06I sensors
- messages are 9b long on passive mode and 24b bit long on active mode
- active mode is not pupported
"""

import struct
from dataclasses import dataclass, field
from typing import Tuple

from pms import SensorWarmingUp, WrongMessageChecksum, WrongMessageFormat

from .. import base
from . import mhz19b

ALIASES = ("ZH03B", "ZH06I")

commands = base.Commands(
    passive_read=base.Cmd(b"\xFF\x01\x86\x00\x00\x00\x00\x00\x79", b"\xFF\x86", 9),
    passive_mode=base.Cmd(b"\xFF\x01\x78\x41\x00\x00\x00\x00\x46", b"", 0),
    active_mode=base.Cmd(b"\xFF\x01\x78\x40\x00\x00\x00\x00\x47", b"\xFF\x86", 9),
    sleep=base.Cmd(b"\xFF\x01\xA7\x01\x00\x00\x00\x00\x57", b"\xFF\xA7", 9),
    wake=base.Cmd(b"\xFF\x01\xA7\x00\x00\x00\x00\x00\x58", b"\xFF\xA7", 9),
)


class Message(mhz19b.Message):
    """Messages from Winsen ZH03B/ZH06I sensors"""

    data_records = slice(0, 3)


@dataclass(frozen=False)
class ObsData(base.ObsData):
    """
    Winsen ZH03B and ZH06-I sensor observations

    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]

    String formats: pm (default), csv and header
    """

    pm25: int = field(metadata=base.metadata("PM2.5", "μg/m3", "concentration"))
    pm10: int = field(metadata=base.metadata("PM10", "μg/m3", "concentration"))
    pm01: int = field(metadata=base.metadata("PM1", "μg/m3", "concentration"))

    @property
    def pm1(self) -> int:
        return self.pm01

    @property
    def pm2_5(self) -> int:
        return self.pm25

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"{self.date:%F %T}: PM1 {self.pm01:.1f}, PM2.5 {self.pm25:.1f}, PM10 {self.pm10:.1f} μg/m3"
        if spec == "csv":
            return f"{self.time}, {self.pm01:.1f}, {self.pm25:.1f}, {self.pm10:.1f}"

        return super().__format__(spec)
