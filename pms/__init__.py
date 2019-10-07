"""
PyPMS logging and recoverable errors
"""
__version__ = "0.1.4"


import logging, os

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
