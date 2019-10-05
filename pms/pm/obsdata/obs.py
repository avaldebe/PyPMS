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
        if spec.endswith("pm"):
            d = spec[:-2] + "d"
            return f"PM1 {self.pm01:{d}}, PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = spec[:-3] + "d"
            return f"{self.raw01:{d}}, {self.raw25:{d}}, {self.raw10:{d}}, {self.pm01:{d}}, {self.pm25:{d}}, {self.pm10:{d}}"
        if spec.endswith("cf"):
            d = (spec[:-2] or ".0") + "%"
            return f"CF1 {self.cf01:{d}}, CF2.5 {self.cf25:{d}}, CF10 {self.cf10:{d}}"
        if spec.endswith("raw"):
            d = spec[:-3] + "d"
            return f"PM1 {self.raw01:{d}}, PM2.5 {self.raw25:{d}}, PM10 {self.raw10:{d}} ug/m3"
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
        if spec.endswith("pm"):
            d = (spec[:-2] or ".1") + "f"
            return f"PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = (spec[:-3] or ".1") + "f"
            return f"{self.pm25:{d}}, {self.pm10:{d}}"
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
        if spec.endswith("pm"):
            d = spec[:-2] + "d"
            return f"PM2.5 {self.pm25:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = spec[:-3] + "d"
            return f"{self.pm25:{d}}, {self.pm10:{d}}"
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
        if spec.endswith("pm"):
            d = (spec[:-2] or "0.2") + "f"
            return f"PM1 {self.pm01:{d}}, PM2.5 {self.pm25:{d}}, PM4 {self.pm04:{d}}, PM10 {self.pm10:{d}} ug/m3"
        if spec.endswith("csv"):
            d = (spec[:-3] or "0.2") + "f"
            return f"{self.pm01:{d}}, {self.pm25:{d}}, {self.pm04:{d}}, {self.pm10:{d}}"
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
        if spec.endswith("pm"):
            d = spec[:-2] + "d"
            return f"PM100 {self.pm100:{d}} ug/m3"
        if spec.endswith("csv"):
            d = spec[:-3] + "d"
            return f"{self.pm100:{d}}"
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
        if spec.endswith("num"):
            d = (spec[:-3] or ".2") + "f"
            return f"N0.3 {self.n0_3:{d}}, N0.5 {self.n0_5:{d}}, N1.0 {self.n1_0:{d}}, N2.5 {self.n2_5:{d}}, N5.0 {self.n5_0:{d}}, N10 {self.n10_0:{d}} #/cm3"
        if spec.endswith("csv"):
            d = spec[:-3] + ".2f"
            return f"{self.n0_3:{d}}, {self.n0_5:{d}}, {self.n1_0:{d}}, {self.n2_5:{d}}, {self.n5_0:{d}}, {self.n10_0:{d}}"
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
        if spec.endswith("csv"):
            d = (spec[:-3] or ".2") + "f"
            return f"{self.n0_5:{d}}, {self.n1_0:{d}}, {self.n2_5:{d}}, {self.n4_0:{d}}, {self.n10_0:{d}}"
        if spec.endswith("num"):
            d = (spec[:-3] or ".2") + "f"
            return f"N0.5 {self.n0_5:{d}}, N1.0 {self.n1_0:{d}}, N2.5 {self.n2_5:{d}}, N4.0 {self.n4_0:{d}}, N10 {self.n10_0:{d}} #/cm3"
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
        if spec.endswith("csv"):
            d = (spec[:-3] or ".2") + "f"
            return f"{self.diam:{d}}"
        if spec.endswith("num"):
            d = (spec[:-3] or ".2") + "f"
            return f"Ø {self.diam:{d}} μm"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
