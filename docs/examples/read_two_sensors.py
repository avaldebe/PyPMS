"""
Read PMSx003 sensor on /dev/ttyUSB0
and MCU680 sensor on /dev/ttyUSB1

Read 4 samples from each sensor, one sample every 20 seconds,
and print the observations on different formats.
"""

from pms.core import SensorReader

pms = SensorReader("PMSx003", "/dev/ttyUSB0", interval=20, samples=4)
bme = SensorReader("MCU680", "/dev/ttyUSB1", interval=20, samples=4)


print("\nPMSx003 and MCU680, 4 samples each on default formats")
with pms, bme:
    for pm, bm in zip(pms(), bme()):
        print(pm)
        print(bm)

print("\nPMSx003 and MCU680, 4 samples each on CSV format")
with pms, bme:
    for pm, bm in zip(pms(), bme()):
        print(f"PMSx003, {pm:csv}, MCU680, {bm:csv}")

print("\nPMSx003 and MCU680, 4 samples each on CSV format with header")
with pms, bme:
    print_header = True
    for pm, bm in zip(pms(), bme()):
        if print_header:
            print(f"PMSx003, {pm:header}, MCU680, {bm:header}")
            print_header = False
        print(f"PMSx003, {pm:csv}, MCU680, {bm:csv}")
