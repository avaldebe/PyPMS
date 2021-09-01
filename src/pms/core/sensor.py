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

from pms import (
    InconsistentObservation,
    SensorWarmingUp,
    WrongMessageChecksum,
    WrongMessageFormat,
    logger,
)

from .types import Cmd, Commands, Message, ObsData


class Sensor(Enum):
    """Sensor modules

    sensor modules are loaded from plugins (entry points) advertized as `"pypms.sensors"`
    """

    _ignore_ = "ep alias Sensor"

    Sensor = vars()
    for ep in metadata.entry_points(group="pypms.sensors"):
        Sensor[ep.name] = ep.load()

        if not hasattr(Sensor[ep.name], "ALIASES"):
            continue

        for alias in Sensor[ep.name].ALIASES:
            Sensor[alias] = Sensor[ep.name]

    def __str__(self) -> str:
        return self.name

    @property
    def Message(self) -> Message:
        return self.value.Message

    @property
    def Data(self) -> ObsData:
        return self.value.ObsData

    @property
    def Commands(self) -> Commands:
        return self.value.commands

    @property
    def baud(self) -> int:
        if hasattr(self.value, "BAUD"):
            return self.value.BAUD
        return 9600

    @property
    def pre_heat(self) -> int:
        if hasattr(self.value, "PREHEAT"):
            return self.value.PREHEAT
        return 0

    @staticmethod
    def now() -> int:  # pragma: no cover
        """current time as seconds since epoch"""
        return int(datetime.now().timestamp())

    def command(self, cmd: str) -> Cmd:
        """Serial command for sensor"""
        return getattr(self.Commands, cmd)

    def check(self, buffer: bytes, command: str) -> bool:
        """Validate buffer contents"""
        try:
            self.Message.decode(buffer, self.command(command))
        except (WrongMessageFormat, WrongMessageChecksum) as e:
            logger.debug(f"decode error {e}")
            return False
        except (SensorWarmingUp, InconsistentObservation) as e:
            logger.debug(f"decode error {e}")
            return True
        else:
            return True

    def decode(self, buffer: bytes, *, time: int = None) -> ObsData:
        """Exract observations from serial buffer"""
        if not time:  # pragma: no cover
            time = self.now()

        data = self.Message.decode(buffer, self.Commands.passive_read)
        return self.Data(time, *data)  # type: ignore[operator]


class Supported(str, Enum):
    """Supported sensor names"""

    _ignore_ = "s Supported"

    Supported = vars()
    for s in Sensor:
        Supported[s.name] = s.name

    default = "PMSx003"
