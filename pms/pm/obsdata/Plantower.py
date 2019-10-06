"""
Observations from Plantower messages

- PMSx003 PM1/PM2.5/PM10 and 6 number concentrations
- PMS3003 PM1/PM2.5/PM10
"""

from dataclasses import dataclass
from typing import Dict
from .obs import Time, RawPM6, RawNum6


@dataclass(frozen=False)
class PMSx003(RawNum6, RawPM6, Time):
    """PMSx003 observations
    
    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [ug/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [ug/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations under X.Y um [#/cm3]
    """

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm01": self.pm01, "pm25": self.pm25, "pm10": self.pm10}
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __format__(self, spec: str) -> str:
        if spec.endswith(("pm", "raw", "cf")):
            pm = RawPM6.__format__(self, spec)
            return f"{self.date:%F %T}: {pm}"
        if spec.endswith("csv"):
            pm = RawPM6.__format__(self, spec)
            num = RawNum6.__format__(self, spec)
            return f"{self.time}, {pm}, {num}"
        if spec.endswith("num"):
            num = RawNum6.__format__(self, spec)
            return f"{self.date:%F %T}: {num}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )


@dataclass(frozen=False)
class PMS3003(RawPM6, Time):
    """PMS3003 observations
    
    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [ug/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [ug/m3]
    """

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm01": self.pm01, "pm25": self.pm25, "pm10": self.pm10}
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __format__(self, spec: str) -> str:
        if spec.endswith(("pm", "raw", "cf")):
            pm = RawPM6.__format__(self, spec)
            return f"{self.date:%F %T}: {pm}"
        if spec.endswith("csv"):
            pm = RawPM6.__format__(self, spec)
            return f"{self.time}, {pm}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
