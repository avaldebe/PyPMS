"""
Read PMSx003 sensor on /dev/ttyUSB0.

Read 4 samples, one sample every 20 seconds,
and print the observations on different formats.
"""

from pms.core import SensorReader

reader = SensorReader("PMSx003", "/dev/ttyUSB0", interval=20, samples=4)

print("\nPMSx003 4 samples on default format")
with reader:
    for obs in reader():
        print(obs)

print("\nPMSx003 4 samples on CSV format")
with reader:
    for obs in reader():
        print(f"{obs:csv}")

print("\nPMSx003 4 samples on CSV format with header")
with reader:
    print_header = True
    for obs in reader():
        if print_header:
            print(f"{obs:header}")
            print_header = False
        print(f"{obs:csv}")
