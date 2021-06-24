# Use as a library

```python
"""Read PMSx003 sensor on /dev/ttyUSB0"""

from pms.core import SensorReader

# read 4 samples, one sample every 15 seconds
reader = SensorReader("PMSx003", "/dev/ttyUSB0", 15, 4)

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
```

## Observation data fields

Each sensor provides different data fields. The `pms -m SENSOR_MODEL info` command will provide information about data fields and it's units.
The following table shows all possible data fields and the type provided by each sensor:

| sensor model    | time  | raw01 | raw25 | raw10 | pm01  | pm25  | pms04 | pm10  | pm100 | n0_3  | n0_5  | n1_0  | n2_5  | n4_0  | n5_0  | n10_0 | HCHO  | temp  | rhum  | pres  | diam  | IAQ_acc |  IAQ  |  gas  |  alt  |
| --------------- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :-----: | :---: | :---: | :---: |
| [`PMS3003`][]   |  int  |  int  |  int  |  int  |  int  |  int  |       |  int  |       | float | float | float | float |       | float | float |
| [`PMSx003`][]   |  int  |  int  |  int  |  int  |  int  |  int  |       |  int  |       | float | float | float | float |       | float | float |
| [`PMS5003S`][]  |  int  |  int  |  int  |  int  |  int  |  int  |       |  int  |       | float | float | float | float |       | float | float |  int  |
| [`PMS5003ST`][] |  int  |  int  |  int  |  int  |  int  |  int  |       |  int  |       | float | float | float | float |       | float | float |  int  | float | float |
| [`PMS5003T`][]  |  int  |  int  |  int  |  int  |  int  |  int  |       |  int  |       | float | float | float | float |       |       |       |       | float | float |
| [`SDS01x`][]    |  int  |       |       |       |       | float |       | float |
| [`SDS198`][]    |  int  |       |       |       |       |       |       |       |  int  |
| [`HPMA115S0`][] |  int  |       |       |       |       |  int  |       |  int  |
| [`HPMA115C0`][] |  int  |       |       |       |  int  |  int  |  int  |  int  |
| [`SPS30`][]     |  int  |       |       |       | float | float | float | float |       |       | float | float | float | float |       | float |       |       |       |       | float |
| [`MCU680`]      |       |       |       |       |       |       |       |       |       |       |       |       |       |       |       |       |       | float | float | float |       |   int   |  int  |  int  |  int  |

[`PMS3003`]:  /docs/sensors/Plantower.md#PMS3003
[`PMSx003`]:  /docs/sensors/Plantower.md#PMSx003
[`PMS5003T`]: /docs/sensors/Plantower.md#PMS5003T
[`PMS5003S`]: /docs/sensors/Plantower.md#PMS5003S
[`PMS5003ST`]:/docs/sensors/Plantower.md#PMS5003ST
[`SDS01x`]:   /docs/sensors/NovaFitness.md#SDS01x
[`SDS198`]:   /docs/sensors/NovaFitness.md#SDS198
[`HPMA115S0`]:/docs/sensors/Honeywell.md#HPMA115S0
[`HPMA115C0`]:/docs/sensors/Honeywell.md#HPMA115C0
[`SPS30`]:    /docs/sensors/Senserion.md#SPS30
[`MCU680`]:   /docs/sensors/mcu680.md#MCU680

On the previous example, `obs` is a [dataclasses.dataclass][] instance which an be inspected as follows

```python
"""Inspect PMSx003 data fields"""

from dataclasses import fields
from typing import Dict
from pms.core import base, Sensor

def types(obs: base.ObsData) -> Dict[str, str]:
    """return a dictionary containing the type of each data field"""""
    return {field.name: field.type for field in fields(obs)}

print(types(Sensor["PMSx003"].Data))
```

[dataclasses.dataclass]: https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass

## Observation formats

As the example at the top of the page shows, the `obs` object has custom formats.
Observations from different sensors support different formats.
The following table shows all different formats

| sensor model  |  csv  | header |  pm   |  num  |  raw  |  cf   |  atm  | hcho  |  bme  | bsec  |
| ------------- | :---: | :----: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| [`PMS3003`]   |   X   |   X    |   X   |   X   |   X   |   X   |       |       |       |       |
| [`PMSx003`]   |   X   |   X    |   X   |   X   |   X   |   X   |       |       |       |       |
| [`PMS5003T`]  |   X   |   X    |   X   |   X   |   X   |   X   |   X   |       |       |       |
| [`PMS5003S`]  |   X   |   X    |   X   |   X   |   X   |   X   |       |   X   |       |       |
| [`PMS5003ST`] |   X   |   X    |   X   |   X   |   X   |   X   |   X   |   X   |       |       |
| [`SDS01x`]    |   X   |   X    |   X   |       |       |       |       |       |       |       |
| [`SDS198`]    |   X   |   X    |   X   |       |       |       |       |       |       |       |
| [`HPMA115S0`] |   X   |   X    |   X   |       |       |       |       |       |       |       |
| [`HPMA115C0`] |   X   |   X    |   X   |       |       |       |       |       |       |       |
| [`SPS30`]     |   X   |   X    |   X   |   X   |       |       |       |       |       |       |
| [`MCU680`]    |   X   |   X    |       |       |       |       |   X   |       |   X   |   X   |
