import warnings

from pms.core import MessageReader, Sensor, SensorReader  # noqa: F401

warnings.warn(
    "the pms.sensor module is deprecated, import from pms.core instead",
    DeprecationWarning,
    stacklevel=2,
)
