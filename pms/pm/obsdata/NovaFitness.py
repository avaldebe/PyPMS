"""
Observations NovaFitness sensors
- SDS01x PM2.5/PM10
- SDS198 PM100
"""

from datetime import datetime
from typing import NamedTuple, Optional, Tuple, Dict


class SDS01x(NamedTuple):
    """SDS01x observations
    
    time                                    measurement time [seconds since epoch]
    raw25, raw10                            PM2.5*10, PM10*10 [ug/m3]
    """

    # seconds since epoch
    time: int
    # rawX [0.1 ug/m3]: PM2.5*10 & PM10*10
    raw25: int
    raw10: int

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm25": self.raw25 / 10, "pm10": self.raw10 / 10}
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
            d = (spec[:-2] or ".1") + "f"
            return f"{self.date:%F %T}: PM2.5 {{pm25:{d}}}, PM10 {{pm10:{d}}} ug/m3".format_map(
                self.subset("pm")
            )
        if spec.endswith("csv"):
            d = (spec[:-3] or ".1") + "f"
            return f"{self.time}, {{pm25:{d}}}, {{pm10:{d}}}".format_map(self.subset("pm"))
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")


class SDS198(NamedTuple):
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

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = (spec[:-2] or ".1") + "f"
            return f"{self.date:%F %T}: PM100 {self.pm100:{d}}"
        if spec.endswith("csv"):
            d = (spec[:-3] or ".1") + "f"
            return f"{self.time}, {self.pm100:{d}}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")
