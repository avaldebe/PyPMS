from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Time:
    """Measurement time [seconds since epoch]"""

    time: int

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)


@dataclass
class RawPM6:
    """Raw and PM values from Plantower sensors
    
    rawX [ug/m3]: raw (cf=1) PM1.0, PM2.5 & PM10 estimate
    pmX  [ug/m3]: PM1.0, PM2.5 & PM10
    """

    raw01: int = field(repr=False)
    raw25: int = field(repr=False)
    raw10: int = field(repr=False)
    pm01: int
    pm25: int
    pm10: int

    # cfX [1]: pmX/rawX
    @property
    def cf01(self) -> float:
        return self._safe_div(self.pm01, self.raw01)

    @property
    def cf25(self) -> float:
        return self._safe_div(self.pm25, self.raw25)

    @property
    def cf10(self) -> float:
        return self._safe_div(self.pm10, self.raw10)

    @staticmethod
    def _safe_div(x: int, y: int) -> float:
        if y:
            return x / y
        if x == y == 0:
            return 1
        return 0

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"PM1 {self.pm01:.1f}, PM2.5 {self.pm25:.1f}, PM10 {self.pm10:.1f} ug/m3"
        if spec == "csv":
            return f"{self.raw01}, {self.raw25}, {self.raw10}, {self.pm01:.1f}, {self.pm25:.1f}, {self.pm10:.1f}"
        if spec == "cf":
            return f"CF1 {self.cf01:.0%}, CF2.5 {self.cf25:.0%}, CF10 {self.cf10:.0%}"
        if spec == "raw":
            return f"PM1 {self.raw01}, PM2.5 {self.raw25}, PM10 {self.raw10} ug/m3"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")


@dataclass
class RawPM2:
    """Raw and PM values from NovaFitness sensors
    
    pmX [ug/m3]: PM2.5 & PM10 (read as 10*pmX)
    """

    pm25: float
    pm10: float

    def __post_init__(self):
        """Convert from 0.1 ug/m3 to ug/m3"""
        self.pm25 /= 10
        self.pm10 /= 10

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"PM2.5 {self.pm25:.1f}, PM10 {self.pm10:.1f} ug/m3"
        if spec == "csv":
            return f"{self.pm25:.1f}, {self.pm10:.1f}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")


@dataclass
class PM2:
    """PM values from Honeywell sensors
    
    pmX [ug/m3]: PM2.5 & PM10
    """

    pm25: int
    pm10: int

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"PM2.5 {self.pm25:.1f}, PM10 {self.pm10:.1f} ug/m3"
        if spec == "csv":
            return f"{self.pm25:.1f}, {self.pm10:.1f}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")


@dataclass
class PM4:
    """PM values from Honeywell and Senserion sensors
    
    pmX [ug/m3]: PM1.0, PM2.5, PM4.0 & PM10
    """

    pm01: float
    pm25: float
    pm04: float
    pm10: float

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"PM1 {self.pm01:.1f}, PM2.5 {self.pm25:.1f}, PM4 {self.pm04:.1f}, PM10 {self.pm10:.1f} ug/m3"
        if spec == "csv":
            return f"{self.pm01:.1f}, {self.pm25:.1f}, {self.pm04:.1f}, {self.pm10:.1f}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")


@dataclass
class PM100:
    """PM100 from NovaFitness sensors
    
    pmX [ug/m3]: PM100
    """

    pm100: int

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"PM100 {self.pm100:.1f} ug/m3"
        if spec == "csv":
            return f"{self.pm100:.1f}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )

    def __str__(self):
        return self.__format__("pm")


@dataclass
class RawNum6:
    """Number concentrations from Plantower sensors
    
    nX_Y [#/cm3]: number concentrations under X.Y um (read as 100*nX_Y)
    """

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

    def __format__(self, spec: str) -> str:
        if spec == "csv":
            return f"{self.n0_3:.2f}, {self.n0_5:.2f}, {self.n1_0:.2f}, {self.n2_5:.2f}, {self.n5_0:.2f}, {self.n10_0:.2f}"
        if spec == "num":
            return f"N0.3 {self.n0_3:.2f}, N0.5 {self.n0_5:.2f}, N1.0 {self.n1_0:.2f}, N2.5 {self.n2_5:.2f}, N5.0 {self.n5_0:.2f}, N10 {self.n10_0:.2f} #/cm3"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )


@dataclass
class Num5:
    """Number concentrations from Plantower sensors
    
    nX_Y [#/cm3]: number concentrations under X.Y um
    """

    n0_5: float
    n1_0: float
    n2_5: float
    n4_0: float
    n10_0: float

    def __format__(self, spec: str) -> str:
        if spec == "csv":
            return f"{self.n0_5:.2f}, {self.n1_0:.2f}, {self.n2_5:.2f}, {self.n4_0:.2f}, {self.n10_0:.2f}"
        if spec == "num":
            return f"N0.5 {self.n0_5:.2f}, N1.0 {self.n1_0:.2f}, N2.5 {self.n2_5:.2f}, N4.0 {self.n4_0:.2f}, N10 {self.n10_0:.2f} #/cm3"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )


@dataclass
class PSize:
    """Typical particle size from Senserion sensors
    
    diam [μm]: typical particle size
    """

    diam: float

    def __format__(self, spec: str) -> str:
        if spec == "csv":
            return f"{self.diam:.1f}"
        if spec == "diam":
            return f"Ø {self.diam:.1f} μm"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
