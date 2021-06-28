import warnings

from pms.core import MessageReader, Sensor, SensorReader

warnings.warn(
    "the pms.sensor module is deprecated, import from pms.core instead",
    DeprecationWarning,
    stacklevel=2,
)
