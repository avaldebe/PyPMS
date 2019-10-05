"""
Observations from Plantower messages

- PMSx003 PM1/PM2.5/PM10 and 6 number concentrations
- PMS3003 PM1/PM2.5/PM10
"""

from datetime import datetime
from typing import NamedTuple, Dict, Optional


class PMSx003(NamedTuple):
    """PMSx003 observations
    
    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [ug/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [ug/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations under X.Y um [#/100cc]
    """

    # seconds since epoch
    time: int
    # rawX [ug/m3]: raw (cf=1) PM1.0, PM2.5 & PM10 estimate
    raw01: int
    raw25: int
    raw10: int
    # pmX [ug/m3]: PM1.0, PM2.5 & PM10
    pm01: int
    pm25: int
    pm10: int
    # nX_Y [#/100cc]: number concentrations under X.Y um
    n0_3: Optional[int] = None
    n0_5: Optional[int] = None
    n1_0: Optional[int] = None
    n2_5: Optional[int] = None
    n5_0: Optional[int] = None
    n10_0: Optional[int] = None

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm01": self.pm01, "pm25": self.pm25, "pm10": self.pm10}
        if spec == "cf":
            return {
                "cf01": self._safe_div(self.pm01, self.raw01),
                "cf25": self._safe_div(self.pm25, self.raw25),
                "cf10": self._safe_div(self.pm10, self.raw10),
            }
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    @staticmethod
    def _safe_div(x: int, y: int) -> float:
        if y:
            return x / y
        if x == y == 0:
            return 1
        return 0

    def __format__(self, spec: str) -> str:
        d = f = None
        if spec.endswith("pm"):
            d = spec[:-2] + "d"
            return f"{self.date:%F %T}: PM1 {self.pm01:{d}}, PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = spec[:-3] + "d"
            f = f"{self.time}, {{1}}, {{2}}, {{3}}, {{4}}, {{5}}, {{6}}, {{7}}, {{8}}, {{9}}, {{10}}, {{11}}, {{12}}"
        elif spec.endswith("num"):
            d = spec[:-3] + "d"
            f = f"{self.date:%F %T}: N0.3 {{7}}, N0.5 {{8}}, N1.0 {{9}}, N2.5 {{10}}, N5.0 {{11}}, N10 {{12}} #/100cc"
        elif spec.endswith("cf"):
            d = (spec[:-2] or ".0") + "%"
            return f"{self.date:%F %T}: CF1 {{cf01:{d}}}, CF2.5 {{cf25:{d}}}, CF10 {{cf10:{d}}}".format_map(
                self.subset("cf")
            )
        if d and f:
            return f.format(*(f"{x:{d}}" if x is not None else "" for x in self))
        else:
            raise ValueError(
                f"Unknown format code '{spec}' "
                f"for object of type '{__name__}.{self.__class__.__name__}'"
            )

    def __str__(self):
        return self.__format__("pm")


class PMS3003(PMSx003):
    pass
