from loguru import logger

from ._version import __version__  # noqa: F401

logger.disable("pms")  # disable logging by default


class SensorWarning(UserWarning):
    """Recoverable errors"""

    pass


class WrongMessageFormat(SensorWarning):
    """Wrongly formatted message: throw away observation"""

    pass


class WrongMessageChecksum(SensorWarning):
    """Failed message checksum: throw away observation"""

    pass


class SensorNotReady(SensorWarning):
    """Sensor not ready to read: observations not reliable"""

    pass


class SensorWarmingUp(SensorNotReady):
    """Empty message: throw away observation and wait until sensor warms up"""

    pass


class InconsistentObservation(SensorNotReady):
    """Message payload makes no sense: throw away observation"""

    pass
