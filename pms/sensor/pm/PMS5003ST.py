"""
Plantower PMS5003ST sensors
- messages are 32b long
- 6 size bins (as PMS5003). HCHO concentration, temperature and relative humidity
"""
from dataclasses import dataclass
from typing import Dict
from . import base, PMS3003, PMSx003, PMS5003S


commands = base.Commands(
    passive_read=PMSx003.commands.passive_read._replace(answer_length=40),
    passive_mode=PMSx003.commands.passive_mode,
    active_mode=PMSx003.commands.active_mode._replace(answer_length=40),
    sleep=PMSx003.commands.sleep,
    wake=PMSx003.commands.wake._replace(answer_length=40),
)


class Message(PMS3003.Message):
    """Messages from Plantower PMS5003ST sensors"""

    data_records = slice(15)


@dataclass(frozen=False)
class ObsData(PMS5003S.ObsData):
    """Observations from Plantower PMS5003ST sensors
    
    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [ug/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [ug/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations under X.Y um [#/cm3]
    HCHO                                    formaldehyde concentration [ug/m3]
    temp                                    temperature [°C]
    rhum                                    relative humidity [%]
    """

    # temp[°C],rhum[%]: temperature,relative humidity (read as 10*temp,10*rhum)
    temp: float
    rhum: float

    def __post_init__(self):
        """Units conversion
        nX_Y [#/cm3] read in [#/0.1L]
        temp [°C]    read in [0.1 °C]
        rhum [%]     read in [1/1000]
        """
        super().__post_init__()
        self.temp /= 10
        self.rhum /= 10

    def __format__(self, spec: str) -> str:
        if spec in ["pm", "raw", "cf", "num", "hcho"]:
            return super().__format__(spec)
        if spec == "csv":
            csv = super().__format__(spec)
            return f"{csv}, {self.temp:.1f}, {self.rhum:.1f}"
        if spec == "atm":
            return f"{self.date:%F %T}: Temp. {self.temp:.1f} °C, Rel.Hum. {self.rhum:.1f} %"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
