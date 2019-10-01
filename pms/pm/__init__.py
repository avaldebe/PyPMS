from .sensor import Sensor
from .reader import SensorReader

SUPPORTED = [s.name for s in Sensor]
DEFAULT = Sensor.Default.name
