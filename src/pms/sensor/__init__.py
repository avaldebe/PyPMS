from pms import logger
from pms.core import MessageReader, Sensor, SensorReader

logger.warning(
    f"the pms.sensor module is deprecated, import from pms.core instead",
    DeprecationWarning,
    2,
)
