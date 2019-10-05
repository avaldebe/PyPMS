"""
Observations NovaFitness sensors

- SDS01x PM2.5/PM10
- SDS198 PM100
"""

from dataclasses import dataclass
from typing import Dict
from .obs import Time, RawPM2, PM100


@dataclass
class SDS01x(RawPM2, Time):
    """SDS01x observations
    
    time                                    measurement time [seconds since epoch]
    raw25, raw10                            PM2.5*10, PM10*10 [ug/m3]
    """

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm25": self.pm25, "pm10": self.pm10}
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __format__(self, spec: str) -> str:
        if spec.endswith("pm"):
            pm = RawPM2.__format__(self, spec)
            return f"{self.date:%F %T}: {pm}"
        if spec.endswith("csv"):
            pm = RawPM2.__format__(self, spec)
            return f"{self.time}, {pm}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )


class SDS198(PM100, Time):

    """SDS198 observations
    
    time                                    measurement time [seconds since epoch]
    pm100                                   PM100 [ug/m3]
    """

    # seconds since epoch
    time: int
    # rawX [ug/m3]: PM100
    pm100: int

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm100": self.pm100}
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __format__(self, spec: str) -> str:
        if spec.endswith("pm"):
            pm = PM100.__format__(self, spec)
            return f"{self.date:%F %T}: {pm}"
        if spec.endswith("csv"):
            pm = PM100.__format__(self, spec)
            return f"{self.time}, {pm}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
