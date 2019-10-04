"""
Observations Honeywell sensors

- HPMA115S0 PM2.5/PM10
- HPMA115C0 PM1/PM2.5/PM4/PM10
"""

from datetime import datetime
from typing import NamedTuple, Optional, Tuple, Dict


class HPMA115S0(NamedTuple):
    """HPMA115S0 observations
    
    time                                    measurement time [seconds since epoch]
    pm25, pm10                              PM2.5, PM10 [ug/m3]
    """

    # seconds since epoch
    time: int
    # pmX [ug/m3]: PM2.5 & PM10
    pm25: int
    pm10: int

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm25": self.pm25, "pm10": self.pm10}
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = spec[:-2] + "d"
            return f"{self.date:%F %T}: PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = spec[:-3] + "d"
            return f"{self.time}, {self.pm25:{d}}, {self.pm10:{d}}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")


class HPMA115C0(NamedTuple):
    """HPMA115C0 observations
    
    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm04, pm10                  PM1.0, PM2.5, PM4.0 PM10 [ug/m3]
    """

    # seconds since epoch
    time: int
    # pmX [ug/m3]: PM2.5 & PM10
    pm01: int
    pm25: int
    pm04: int
    pm10: int

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm01": self.pm01, "pm25": self.pm25, "pm04": self.pm04, "pm10": self.pm10}
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = spec[:-2] + "d"
            return f"{self.date:%F %T}: PM1 {self.pm01:{d}}, PM2.5 {self.pm25:{d}}, PM4 {self.pm04:{d}},PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = spec[:-3] + "d"
            return (
                f"{self.time}, {self.pm01:{d}}, {self.pm25:{d}}, {self.pm04:{d}}, {self.pm10:{d}}"
            )
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")
