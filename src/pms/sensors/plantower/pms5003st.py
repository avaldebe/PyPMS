"""
Plantower PMS5003ST sensors
- messages are 40b long
- 6 size bins (as PMS5003). HCHO concentration, temperature and relative humidity
"""

import struct
from dataclasses import dataclass, field
from typing import Tuple

from .. import base
from . import pms3003, pms5003s, pmsx003

commands = base.Commands(
    passive_read=base.Cmd(pmsx003.commands.passive_read.command, b"\x42\x4D\x00\x24", 40),
    passive_mode=pmsx003.commands.passive_mode,
    active_mode=base.Cmd(pmsx003.commands.active_mode.command, b"\x42\x4D\x00\x24", 40),
    sleep=pmsx003.commands.sleep,
    wake=base.Cmd(pmsx003.commands.wake.command, b"\x42\x4D\x00\x24", 40),
)


class Message(pms3003.Message):
    """Messages from Plantower PMS5003ST sensors"""

    data_records = slice(15)

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        if len(message) == 34:
            # 14th record is signed (temp)
            return struct.unpack(f">13Hh3H", message)
        else:
            return pms3003.Message._unpack(message)


@dataclass(frozen=False)
class ObsData(pms5003s.ObsData):
    """
    Plantower PMS5003ST sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations over X.Y um [#/cm3]
    HCHO                                    formaldehyde concentration [mg/m3]
    temp                                    temperature [°C]
    rhum                                    relative humidity [%]

    String formats: pm (default), raw, cf, num, hcho, atm, csv and header
    """

    # temp[°C],rhum[%]: temperature,relative humidity (read as 10*temp,10*rhum)
    temp: float = field(metadata=base.metadata("temperature", "°C", "degrees"))
    rhum: float = field(metadata=base.metadata("relative humidity", "%", "percentage"))

    def __post_init__(self):
        """Units conversion
        nX_Y [#/cm3] read in [#/0.1L]
        HCHO [mg/m3] read in [μg/m3]
        temp [°C]    read in [0.1 °C]
        rhum [%]     read in [1/1000]
        """
        super().__post_init__()
        self.temp /= 10
        self.rhum /= 10

    def __format__(self, spec: str) -> str:
        if spec == "csv":
            csv = super().__format__(spec)
            return f"{csv}, {self.temp:.1f}, {self.rhum:.1f}"
        if spec == "atm":
            return f"{self.date:%F %T}: Temp. {self.temp:.1f} °C, Rel.Hum. {self.rhum:.1f} %"

        return super().__format__(spec)
