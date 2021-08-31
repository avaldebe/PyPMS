# Use as a library

`PyPMS`/`pms` is meant as a command line application.
This section contain some help for those brave enough to use its internals as a library.

## Basic examples


=== "read one sensor"

    ``` python
    --8<-- "read_one_sensor.py"
    ```

    ```
    --8<-- "read_one_sensor.out"
    ```


=== "read two sensors"

    ``` python
    --8<-- "read_two_sensors.py"
    ```

    ```
    --8<-- "read_two_sensors.out"
    ```


## Observation data fields

Each sensor provides different data fields. The `pms -m SENSOR_MODEL info` command will provide information about data fields and their units.
The following table shows all possible data fields and the type provided by each sensor:

=== "particulate matter"

    | `--sensor-model` | pm01  | pm25  | pms04 | pm10  | pm100 | raw01 | raw25 | raw10 |
    | ---------------- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
    | [PMS3003]        |  int  |  int  |       |  int  |       |  int  |  int  |  int  |
    | [PMSx003]        |  int  |  int  |       |  int  |       |  int  |  int  |  int  |
    | [PMS5003S]       |  int  |  int  |       |  int  |       |  int  |  int  |  int  |
    | [PMS5003ST]      |  int  |  int  |       |  int  |       |  int  |  int  |  int  |
    | [PMS5003T]       |  int  |  int  |       |  int  |       |  int  |  int  |  int  |
    | [SDS01x]         |       | float |       | float |
    | [SDS198]         |       |       |       |       |  int  |
    | [HPMA115S0]      |       |  int  |       |  int  |
    | [HPMA115C0]      |  int  |  int  |  int  |  int  |
    | [SPS30]          | float | float | float | float |
    | [ZH0xx]          |  int  |  int  |       |  int  |
    | [MHZ19B]         |
    | [MCU680]         |

=== "number count"

    | `--sensor-model` | n0_3  | n0_5  | n1_0  | n2_5  | n4_0  | n5_0  | n10_0 |
    | ---------------- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
    | [PMS3003]        | float | float | float | float |       | float | float |
    | [PMSx003]        | float | float | float | float |       | float | float |
    | [PMS5003S]       | float | float | float | float |       | float | float |
    | [PMS5003ST]      | float | float | float | float |       | float | float |
    | [PMS5003T]       | float | float | float | float |       |       |       |
    | [SDS01x]         |
    | [SDS198]         |
    | [HPMA115S0]      |
    | [HPMA115C0]      |
    | [SPS30]          |       | float | float | float | float |       | float |
    | [ZH0xx]          |
    | [MHZ19B]         |
    | [MCU680]         |

=== "environmental"

    | `--sensor-model` | time  | temp  | rhum  | pres  | HCHO  |  CO2  |
    | ---------------- | :---: | :---: | :---: | :---: | :---: | :---: |
    | [PMS3003]        |  int  |
    | [PMSx003]        |  int  |
    | [PMS5003S]       |  int  |       |       |       |  int  |
    | [PMS5003ST]      |  int  | float | float |       |  int  |
    | [PMS5003T]       |  int  | float | float |
    | [SDS01x]         |  int  |       |
    | [SDS198]         |  int  |       |
    | [HPMA115S0]      |  int  |       |
    | [HPMA115C0]      |  int  |       |
    | [SPS30]          |  int  |       |       |       |
    | [ZH0xx]          |  int  |       |
    | [MHZ19B]         |  int  |       |       |       |       |  int  |
    | [MCU680]         |  int  | float | float | float |

=== "other"

    | `--sensor-model` | diam  | IAQ_acc |  IAQ  |  gas  |  alt  |
    | ---------------- | :---: | :-----: | :---: | :---: | :---: |
    | [PMS3003]        |
    | [PMSx003]        |
    | [PMS5003S]       |
    | [PMS5003ST]      |
    | [PMS5003T]       |
    | [SDS01x]         |
    | [SDS198]         |
    | [HPMA115S0]      |
    | [HPMA115C0]      |
    | [SPS30]          | float |
    | [ZH0xx]          |
    | [MHZ19B]         |
    | [MCU680]         |       |   int   |  int  |  int  |  int  |

[PMS3003]:  sensors/Plantower.md#pms3003
[PMSx003]:  sensors/Plantower.md#pmx3003
[PMS5003T]: sensors/Plantower.md#pms5003t
[PMS5003S]: sensors/Plantower.md#pms5003s
[PMS5003ST]:sensors/Plantower.md#pms5003St
[SDS01x]:   sensors/NovaFitness.md#sds01x
[SDS198]:   sensors/NovaFitness.md#sds198
[HPMA115S0]:sensors/Honeywell.md#hpma115s0
[HPMA115C0]:sensors/Honeywell.md#hpma115c0
[SPS30]:    sensors/Sensirion.md#sps30
[ZH0xx]:    sensors/Winsen.md#zh0xx
[MHZ19B]:   sensors/Winsen.md#mhz19b
[MCU680]:   sensors/mcu680.md#mcu680

On the previous example, `obs` is a [dataclasses.dataclass] instance which an be inspected as follows

``` python
--8<-- "inspect_data_fields.py"
```

```
--8<-- "inspect_data_fields.out"
```

[dataclasses.dataclass]: https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass

## Observation formats

As the example at the top of the page shows, the `obs` object has custom formats.
Observations from different sensors support different formats.
The following table shows all different formats

| `--sensor-model` |       csv        |      header      |        pm        |       num        |       raw        |        cf        |       atm        |       hcho       |       co2        |       bme        |       bsec       |
| ---------------- | :--------------: | :--------------: | :--------------: | :--------------: | :--------------: | :--------------: | :--------------: | :--------------: | :--------------: | :--------------: | :--------------: |
| [PMS3003]        | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |                  |
| [PMSx003]        | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |                  |
| [PMS5003T]       | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |
| [PMS5003S]       | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: |                  | :material-check: |                  |                  |                  |
| [PMS5003ST]      | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: |                  |                  |                  |
| [SDS01x]         | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |                  |                  |                  |                  |
| [SDS198]         | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |                  |                  |                  |                  |
| [HPMA115S0]      | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |                  |                  |                  |                  |
| [HPMA115C0]      | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |                  |                  |                  |                  |
| [SPS30]          | :material-check: | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |                  |                  |                  |
| [ZH0xx]          | :material-check: | :material-check: | :material-check: |
| [MHZ19B]         | :material-check: | :material-check: |                  |                  |                  |                  |                  |                  | :material-check: |
| [MCU680]         | :material-check: | :material-check: |                  |                  |                  |                  | :material-check: |                  |                  | :material-check: | :material-check: |
