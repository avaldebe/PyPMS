"""
NovaFitness SDS198 sensors
- messages are 10b long
- only PM100 measurements
"""
from dataclasses import dataclass, field
from typing import Dict
from . import base, SDS01x

commands = SDS01x.commands


class Message(SDS01x.Message):
    """Messages from NovaFitness SDS011, SDS018 and SDS021 sensors"""

    data_records = slice(1, 2)


@dataclass(frozen=False)
class ObsData(base.ObsData):

    """SDS198 observations
    
    time                                    measurement time [seconds since epoch]
    pm100                                   PM100 [ug/m3]
    """

    pm100: int

    def __format__(self, spec: str) -> str:
        if spec == "header":
            return super().__format__(spec)
        if spec.endswith("pm"):
            return f"{self.date:%F %T}: PM100 {self.pm100:.1f} ug/m3"
        if spec.endswith("csv"):
            return f"{self.time}, {self.pm100:.1f}"
        raise ValueError(
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
