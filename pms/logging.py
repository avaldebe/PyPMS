"""
Logging and recoverable errors
"""

import logging, os

logging.basicConfig(level=os.environ.get("LEVEL", "WARNING"))
logger = logging.getLogger("pms")


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
