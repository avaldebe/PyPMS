"""
Access supported PM sensors from a single object
"""


from datetime import datetime
from enum import Enum
from typing import NamedTuple
from pms import logger, WrongMessageFormat
from . import base, pm, aq


class Sensor(Enum):
    """Supported PM sensors"""

    PMSx003 = pm.PMSx003
    PMS3003 = pm.PMS3003
    PMS5003S = pm.PMS5003S
    PMS5003ST = pm.PMS5003ST
    PMS5003T = pm.PMS5003T
    SDS01x = pm.SDS01x
    SDS198 = pm.SDS198
    HPMA115S0 = pm.HPMA115S0
    HPMA115C0 = pm.HPMA115C0
    SPS30 = pm.SPS30
    MCU680 = aq.MCU680

    PMS1003 = PMS5003 = PMS7003 = PMSA003 = PMSx003
    G1, G3, G5, G7, G10 = PMS1003, PMS3003, PMS5003, PMS7003, PMSA003
    SDS011 = SDS018 = SDS021 = SDS01x
    BME680 = MCU680

    @property
    def Message(self) -> base.Message:
        return self.value.Message

    @property
    def Data(self) -> base.ObsData:
        return self.value.ObsData

    @property
    def Commands(self) -> base.Commands:
        return self.value.commands

    @property
    def baud(self) -> int:
        return 115_200 if self.name == "SPS30" else 9600

    @staticmethod
    def now() -> int:  # pragma: no cover
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())

    def command(self, cmd: str) -> base.Cmd:
        """Serial command for sensor"""
        return getattr(self.Commands, cmd)

    def check(self, buffer: bytes, command: str) -> bool:
        """Validate buffer contents"""
        try:
            self.Message.decode(buffer, self.command(command))
        except WrongMessageFormat:
            return False
        else:
            return True

    def decode(self, buffer: bytes, *, time: int = None) -> NamedTuple:
        """Exract observations from serial buffer"""
        if not time:  # pragma: no cover
            time = self.now()

        data = self.Message.decode(buffer, self.Commands.passive_read)
        return self.Data(time, *data)  # type: ignore
