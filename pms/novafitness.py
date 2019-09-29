"""
NovaFitness SDS01x PM2.5/PM10 sensors

The SDS198 PM100 sensor is not supported
"""

import struct
from datetime import datetime
from typing import NamedTuple, Optional, Tuple


class Data(NamedTuple):
    """SDS01x observations
    
    time                                    measurement time [seconds since epoch]
    pm25, pm10                              PM2.5, PM10 [ug/m3]
    """

    # seconds since epoch
    time: int
    # rawX [0.1 ug/m3]: PM2.5*10 & PM10*10
    raw25: int
    raw10: int

    @property
    def pm25(self) -> float:
        """extract PM2.5 (float) from raw25 (int)"""
        return self.raw25 / 10

    @property
    def pm10(self) -> float:
        """extract PM10 (float) from raw25 (int)"""
        return self.raw10 / 10

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = (spec[:-2] or ".1") + "f"
            return f"{self.date:%F %T}: PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = (spec[:-3] or ".1") + "f"
            return f"{self.time}, {self.pm25:{d}}, {self.pm10:{d}}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")

    @staticmethod
    def now() -> int:
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())
