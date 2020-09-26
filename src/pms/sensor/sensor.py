"""
Access supported sensors from a single object
"""

from datetime import datetime
from enum import Enum

from pms import WrongMessageFormat
from pms.sensor import base, plantower, novafitness, honeywell, senserion, bosch_sensortec


class Sensor(Enum):
    """Supported PM sensors"""

    PMSx003 = plantower.pmsx003
    PMS3003 = plantower.pms3003
    PMS5003S = plantower.pms5003s
    PMS5003ST = plantower.pms5003st
    PMS5003T = plantower.pms5003t
    SDS01x = novafitness.sds01x
    SDS198 = novafitness.sds198
    HPMA115S0 = honeywell.hpma115s0
    HPMA115C0 = honeywell.hpma115c0
    SPS30 = senserion.sps30
    MCU680 = bosch_sensortec.mcu680

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
    def baud(self) -> int:  # pragma: no cover
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

    def decode(self, buffer: bytes, *, time: int = None) -> base.ObsData:
        """Exract observations from serial buffer"""
        if not time:  # pragma: no cover
            time = self.now()

        data = self.Message.decode(buffer, self.Commands.passive_read)
        return self.Data(time, *data)  # type: ignore
