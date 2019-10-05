"""
Observations from Senserion messages

- SPS30 PM1/PM2.5/PM4/PM10, 5 number concentrations and typical particle size
"""

from datetime import datetime
from typing import NamedTuple, Dict


class SPS30(NamedTuple):
    """SPS30 observations
    
    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm04, pm10                  PM1.0, PM2.5, PM4.0, PM10 [ug/m3]
    n0_5, n1_0, n2_5, n4_0, n10_0           number concentrations under X.Y um [#/cm3]
    tps                                     typical particle size [μm]
    """

    # seconds since epoch
    time: int
    # pmX [ug/m3]: PM1.0, PM2.5, PM4.0. & PM10
    pm01: float
    pm25: float
    pm04: float
    pm10: float
    # nX_Y [#/cm3]: number concentrations under X.Y um
    n0_5: float
    n1_0: float
    n2_5: float
    n4_0: float
    n10_0: float
    # typical particle size [μm]
    tps: float

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm01": self.pm01, "pm25": self.pm25, "pm04": self.pm04, "pm10": self.pm10}
        if spec == "num":
            return {
                "n0_5": self.n0_5,
                "n1_0": self.n1_0,
                "n2_5": self.n2_5,
                "n4_0": self.n4_0,
                "n10_0": self.n10_0,
            }
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
            return f"{self.date:%F %T}: PM1 {self.pm01:{d}}, PM2.5 {self.pm25:{d}}, PM4.0 {self.pm04:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = (spec[:-3] or ".1") + "f"
            return f"{{}}{', {:{d}}'*10}".format(d=d, *self)
        if spec.endswith("num"):
            d = (spec[:-3] or ".1") + "f"
            return f"{self.date:%F %T}: N0.5 {self.n0_5:{d}}, N1.0 {self.n1_0:{d}}, N2.5 {self.n2_5:{d}}, N4.0 {self.n4_0:{d}}, N10 {self.n10_0:{d}} #/cm3"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")
