"""
Plantower PMS5003S sensors
- messages are 32b long
- 6 size bins (as PMS5003) and HCHO concentration
"""
from dataclasses import dataclass, field
from typing import Dict
from .. import base
from . import PMS3003, PMSx003


commands = PMSx003.commands


class Message(PMS3003.Message):
    """Messages from Plantower PMS5003S sensors"""

    data_records = slice(13)


@dataclass(frozen=False)
class ObsData(PMSx003.ObsData):
    """Observations from Plantower PMS5003S sensors

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [ug/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [ug/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations over X.Y um [#/cm3]
    HCHO                                    formaldehyde concentration [mg/m3]
    """

    # HCHO [mg/m3]: formaldehyde concentration (read as ug/m3, datasheet says 1/1000 mg/m3 ie ug/m3)
    HCHO: int = field(metadata=base.metadata("formaldehyde", "mg/m3", "concentration"))

    def __post_init__(self):
        """Units conversion
        nX_Y [#/cm3] read in [#/0.1L]
        HCHO [mg/m3] read in [ug/m3]
        """
        super().__post_init__()
        self.HCHO /= 1000

    def __format__(self, spec: str) -> str:
        if spec in ["header", "pm", "raw", "cf", "num"]:
            return super().__format__(spec)
        if spec == "csv":
            csv = super().__format__(spec)
            return f"{csv}, {self.HCHO:.3f}"
        if spec == "hcho":
            return f"{self.date:%F %T}: HCHO {self.HCHO:.3f} mg/m3"
        raise ValueError(  # pragma: no cover
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
