"""
Observations from Senserion messages

- SPS30 PM1/PM2.5/PM4/PM10, 5 number concentrations and typical particle size
"""

from dataclasses import dataclass
from typing import Dict
from .obs import Time, PM4, Num5, PSize


@dataclass(frozen=False)
class SPS30(PSize, Num5, PM4, Time):
    """SPS30 observations
    
    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm04, pm10                  PM1.0, PM2.5, PM4.0, PM10 [ug/m3]
    n0_5, n1_0, n2_5, n4_0, n10_0           number concentrations under X.Y um [#/cm3]
    tps                                     typical particle size [μm]
    """

    def subset(self, spec: str) -> Dict[str, float]:
        if spec == "pm":
            return {"pm01": self.pm01, "pm25": self.pm25, "pm04": self.pm04, "pm10": self.pm10}
        raise ValueError(
            f"Unknown subset code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __format__(self, spec: str) -> str:
        if spec.endswith(("pm", "raw", "cf")):
            pm = PM4.__format__(self, spec)
            return f"{self.date:%F %T}: {pm}"
        if spec.endswith("csv"):
            pm = PM4.__format__(self, spec)
            num = Num5.__format__(self, spec)
            diam = PSize.__format__(self, spec)
            return f"{self.time}, {pm}, {num}, {diam}"
        if spec.endswith("num"):
            num = Num5.__format__(self, spec)
            return f"{self.date:%F %T}: {num}"
        if spec.endswith("diam"):
            diam = PSize.__format__(self, spec)
            return f"{self.date:%F %T}: {diam}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
