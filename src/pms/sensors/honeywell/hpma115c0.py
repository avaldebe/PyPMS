"""
Honeywell HPMA115C0 sensors
- passive mode messages are 16b long
- active mode messages are 32b long
"""

from dataclasses import dataclass, field

from .. import base
from . import hpma115s0

commands = hpma115s0.commands._replace(
    passive_read=base.Cmd(  # Read Particle Measuring Results
        b"\x68\x01\x04\x93", b"\x40\x05\x04", 16
    )
)


class Message(hpma115s0.Message):
    """Messages from Honeywell HPMA115C0 sensors"""

    data_records = slice(4)


@dataclass(frozen=False)
class ObsData(base.ObsData):
    """
    Honeywell HPMA115C0 sensor observations

    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm04, pm10                  PM1.0, PM2.5, PM4.0 PM10 [μg/m3]

    String formats: pm (default), csv and header
    """

    pm01: int = field(metadata=base.metadata("PM1", "μg/m3", "concentration"))
    pm25: int = field(metadata=base.metadata("PM2.5", "μg/m3", "concentration"))
    pm04: int = field(metadata=base.metadata("PM4", "μg/m3", "concentration"))
    pm10: int = field(metadata=base.metadata("PM10", "μg/m3", "concentration"))

    @property
    def pm1(self) -> int:
        return self.pm01

    @property
    def pm2_5(self) -> int:
        return self.pm25

    @property
    def pm4(self) -> int:
        return self.pm04

    def __format__(self, spec: str) -> str:
        if spec == "pm":
            return f"{self.date:%F %T}: PM1 {self.pm01:.1f}, PM2.5 {self.pm25:.1f}, PM4 {self.pm04:.1f}, PM10 {self.pm10:.1f} μg/m3"
        if spec == "csv":
            return (
                f"{self.time}, {self.pm01:.1f}, {self.pm25:.1f}, {self.pm04:.1f}, {self.pm10:.1f}"
            )

        return super().__format__(spec)
