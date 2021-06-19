import logging
import os

logging.basicConfig(level=os.getenv("LEVEL", "WARNING"))
logger = logging.getLogger(__name__)


class SensorWarning(UserWarning):
    """Recoverable errors"""

    pass


class WrongMessageFormat(SensorWarning):
    """Wrongly formattted message: throw away observation"""

    pass


class WrongMessageChecksum(SensorWarning):
    """Failed message checksum: throw away observation"""

    pass


class SensorWarmingUp(SensorWarning):
    """Empty message: throw away observation and wait until sensor warms up"""

    pass


class InconsistentObservation(SensorWarning):
    """Message payload makes no sense: throw away observation"""

    pass
