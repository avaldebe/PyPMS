"""
NovaFitness SDS198 sensors
- messages are 10b long
- only PM100 measurements
"""
from dataclasses import dataclass, field
from typing import Dict
from .. import base
from . import SDS01x

commands = SDS01x.commands._replace(
    passive_read=base.Cmd(
        b"\xAA\xB4\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x02\xAB",
        b"\xAA\xCF",
        10,
    )
)


class Message(SDS01x.Message):
    """Messages from NovaFitness SDS011, SDS018 and SDS021 sensors"""

    data_records = slice(1, 2)


@dataclass(frozen=False)
class ObsData(base.ObsData):

    """SDS198 observations

    time                                    measurement time [seconds since epoch]
    pm100                                   PM100 [ug/m3]
    """

    pm100: int = field(metadata=base.metadata("PM100", "ug/m3", "concentration"))

    def __format__(self, spec: str) -> str:
        if spec == "header":
            return super().__format__(spec)
        if spec == "pm":
            return f"{self.date:%F %T}: PM100 {self.pm100:.1f} ug/m3"
        if spec == "csv":
            return f"{self.time}, {self.pm100:.1f}"
        raise ValueError(  # pragma: no cover
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
