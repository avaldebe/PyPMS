"""
Plantower PMS1003, PMS5003, PMS7003 and PMSA003 sensors
- messages are 32b long
"""

import re
from dataclasses import dataclass

from pms import InconsistentObservation

from .. import base
from . import pms3003

ALIASES = ("PMS1003", "G1", "PMS5003", "G5", "PMS7003", "G7", "PMSA003", "G10")


commands = base.Commands(
    passive_read=base.Cmd(b"\x42\x4D\xE2\x00\x00\x01\x71", b"\x42\x4D\x00\x1c", 32),
    passive_mode=base.Cmd(b"\x42\x4D\xE1\x00\x00\x01\x70", b"\x42\x4D\x00\x04", 8),
    active_mode=base.Cmd(b"\x42\x4D\xE1\x00\x01\x01\x71", b"\x42\x4D\x00\x1c", 32),
    sleep=base.Cmd(b"\x42\x4D\xE4\x00\x00\x01\x73", b"\x42\x4D\x00\x04", 8),
    wake=base.Cmd(b"\x42\x4D\xE4\x00\x01\x01\x74", b"\x42\x4D\x00\x1c", 32),
)


class Message(pms3003.Message):
    """Messages from Plantower PMS1003, PMS5003, PMS7003 and PMSA003 sensors"""

    data_records = slice(12)


@dataclass(frozen=False)
class ObsData(pms3003.ObsData):
    """
    Plantower PMS1003, PMS5003, PMS7003 and PMSA003 sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations over X.Y um [#/cm3]

    String formats: pm (default), raw, cf, num, csv and header
    """

    # nX_Y [#/cm3]: number concentrations over X.Y um (read as 100*nX_Y)
    n0_3: float
    n0_5: float
    n1_0: float
    n2_5: float
    n5_0: float
    n10_0: float

    def __post_init__(self):
        """Convert from #/100cm3 to #/cm3"""
        self.n0_3 /= 100
        self.n0_5 /= 100
        self.n1_0 /= 100
        self.n2_5 /= 100
        self.n5_0 /= 100
        self.n10_0 /= 100

        if self.n0_3 == 0 and self.pm10 > 0:
            raise InconsistentObservation(
                f"inconsistent obs: PM10={self.pm10} and N0.3={self.n0_3}"
            )

    def __format__(self, spec: str) -> str:
        if spec == "csv":
            csv = super().__format__(spec)
            return f"{csv}, {self.n0_3:.2f}, {self.n0_5:.2f}, {self.n1_0:.2f}, {self.n2_5:.2f}, {self.n5_0:.2f}, {self.n10_0:.2f}"
        if spec == "num":
            return f"{self.date:%F %T}: N0.3 {self.n0_3:.2f}, N0.5 {self.n0_5:.2f}, N1.0 {self.n1_0:.2f}, N2.5 {self.n2_5:.2f}, N5.0 {self.n5_0:.2f}, N10 {self.n10_0:.2f} #/cm3"
        if spec == "":
            return str(self)

        return super().__format__(spec)
