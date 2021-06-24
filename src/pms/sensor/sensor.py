"""
Access supported sensors from a single object
"""

import sys
from datetime import datetime

if sys.version_info >= (3, 7):  # pragma: no cover
    from enum import Enum
else:  # pragma: no cover
    from aenum import Enum

if sys.version_info >= (3, 10):  # pragma: no cover
    from importlib import metadata
else:  # pragma: no cover
    import importlib_metadata as metadata

from pms import WrongMessageChecksum, WrongMessageFormat
from pms.sensor import base


class Sensor(Enum):
    """Supported sensors"""

    _ignore_ = "ep alias Sensor"

    Sensor = vars()
    for ep in metadata.entry_points(group="pypms.sensors"):
        Sensor[ep.name] = ep.load()

        if not hasattr(Sensor[ep.name], "ALIASES"):
            continue

        for alias in Sensor[ep.name].ALIASES:
            Sensor[alias] = Sensor[ep.name]

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
        if hasattr(self.value, "BAUD"):
            return self.value.BAUD
        return 9600

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
        except (WrongMessageFormat, WrongMessageChecksum):
            return False
        else:
            return True

    def decode(self, buffer: bytes, *, time: int = None) -> base.ObsData:
        """Exract observations from serial buffer"""
        if not time:  # pragma: no cover
            time = self.now()

        data = self.Message.decode(buffer, self.Commands.passive_read)
        return self.Data(time, *data)  # type: ignore
