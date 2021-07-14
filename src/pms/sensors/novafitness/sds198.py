"""
NovaFitness SDS198 sensors
- messages are 10b long
- only PM100 measurements
"""

from dataclasses import dataclass, field

from .. import base
from . import sds01x

commands = sds01x.commands._replace(
    passive_read=base.Cmd(
        b"\xAA\xB4\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x02\xAB",
        b"\xAA\xCF",
        10,
    )
)


class Message(sds01x.Message):
    """Messages from NovaFitness SDS011, SDS018 and SDS021 sensors"""

    data_records = slice(1, 2)


@dataclass(frozen=False)
class ObsData(base.ObsData):

    """
    NovaFitness SDS198 sensor observations

    time                                    measurement time [seconds since epoch]
    pm100                                   PM100 [μg/m3]

    String formats: pm (default), csv and header
    """

    pm100: int = field(metadata=base.metadata("PM100", "μg/m3", "concentration"))

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"{self.date:%F %T}: PM100 {self.pm100:.1f} μg/m3"
        if spec == "csv":
            return f"{self.time}, {self.pm100:.1f}"
        if spec == "":
            return str(self)

        return super().__format__(spec)
