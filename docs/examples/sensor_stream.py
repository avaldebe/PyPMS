"""
Read PMSx003 sensor on /dev/ttyUSB0.

Use a low-level Stream class for more granular
control of the sensor.
"""

from pms.core import SensorStream

stream = SensorStream(sensor="PMSx003", port="/dev/ttyUSB0")

print("\nPMSx003 4 samples on default format")

stream.open()
for _ in range(4):
    print(stream.read())
stream.close()
