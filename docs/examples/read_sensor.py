"""Read PMSx003 sensor on /dev/ttyUSB0"""

from pms.core import SensorReader

# read 4 samples, one sample every 20 seconds
reader = SensorReader("PMSx003", "/dev/ttyUSB0", interval=20, samples=4)

# read 4 samples and print PM fields (default format)
with reader:
    for obs in reader():
        print(obs)

# read 4 samples and print all fields as csv
with reader:
    for obs in reader():
        print(f"{obs:csv}")

# read 4 samples and print as csv with header
with reader:
    print_header = True
    for obs in reader():
        if print_header:
            print(f"{obs:header}")
            print_header = False
        print(f"{obs:csv}")
