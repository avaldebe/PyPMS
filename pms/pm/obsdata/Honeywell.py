"""
Observations Honeywell sensors

- HPMA115S0 PM2.5/PM10
- HPMA115C0 PM1/PM2.5/PM4/PM10
"""

from dataclasses import dataclass
from typing import Dict
from .obs import Time, PM2, PM4


@dataclass
class HPMA115S0(PM2, Time):
    """HPMA115S0 observations
    
    time                                    measurement time [seconds since epoch]
    pm25, pm10                              PM2.5, PM10 [ug/m3]
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
            pm = PM2.__format__(self, spec)
            return f"{self.date:%F %T}: {pm}"
        if spec.endswith("csv"):
            pm = PM2.__format__(self, spec)
            return f"{self.time}, {pm}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )


@dataclass
class HPMA115C0(PM4, Time):
    """HPMA115C0 observations
    
    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm04, pm10                  PM1.0, PM2.5, PM4.0 PM10 [ug/m3]
    """

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm01": self.pm01, "pm25": self.pm25, "pm04": self.pm04, "pm10": self.pm10}
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __format__(self, spec: str) -> str:
        if spec.endswith("pm"):
            pm = PM4.__format__(self, spec)
            return f"{self.date:%F %T}: {pm}"
        if spec.endswith("csv"):
            pm = PM4.__format__(self, spec)
            return f"{self.time}, {pm}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
