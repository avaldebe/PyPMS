"""
Plantower PMS5003T sensors
- messages are 32b long
- only 4 size bins
"""

import struct
from dataclasses import dataclass, field
from typing import Tuple

from pms import InconsistentObservation

from .. import base
from . import pms3003, pmsx003

commands = pmsx003.commands


class Message(pms3003.Message):
    """Messages from Plantower PMS5003T sensors"""

    data_records = slice(12)

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        if len(message) == 26:
            # 11th record is signed (temp)
            return struct.unpack(">10Hh2H", message)
        else:
            return pms3003.Message._unpack(message)


@dataclass(frozen=False)
class ObsData(pms3003.ObsData):
    """
    Plantower PMS5003T sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]
    n0_3, n0_5, n1_0, n2_5                  number concentrations over X.Y um [#/cm3]
    temp                                    temperature [°C]
    rhum                                    relative humidity [%]

    String formats: pm (default), raw, cf, num, atm, csv and header
    """

    # nX_Y [#/cm3]: number concentrations over X.Y um (read as 100*nX_Y)
    n0_3: float
    n0_5: float
    n1_0: float
    n2_5: float
    # temp[°C],rhum[%]: temperature,relative humidity (read as 10*temp,10*rhum)
    temp: float = field(metadata=base.metadata("temperature", "°C", "degrees"))
    rhum: float = field(metadata=base.metadata("relative humidity", "%", "percentage"))

    def __post_init__(self):
        """Units conversion
        nX_Y [#/cm3] read in [#/0.1L]
        temp [°C]    read in [0.1 °C]
        rhum [%]     read in [1/1000]
        """
        self.n0_3 /= 100
        self.n0_5 /= 100
        self.n1_0 /= 100
        self.n2_5 /= 100
        self.temp /= 10
        self.rhum /= 10

        if self.n0_3 == 0 and self.pm10 > 0:
            raise InconsistentObservation(
                f"inconsistent obs: PM10={self.pm10} and N0.3={self.n0_3}"
            )

    def __format__(self, spec: str) -> str:
        if spec == "csv":
            pm = super().__format__(spec)
            return f"{pm}, {self.n0_3:.2f}, {self.n0_5:.2f}, {self.n1_0:.2f}, {self.n2_5:.2f}, {self.temp:.1f}, {self.rhum:.1f}"
        if spec == "num":
            return f"{self.date:%F %T}: N0.3 {self.n0_3:.2f}, N0.5 {self.n0_5:.2f}, N1.0 {self.n1_0:.2f}, N2.5 {self.n2_5:.2f} #/cm3"
        if spec == "atm":
            return f"{self.date:%F %T}: Temp. {self.temp:.1f} °C, Rel.Hum. {self.rhum:.1f} %"

        return super().__format__(spec)
