# Serial Air Quality Sensors

Data acquisition and logging for Air Quality Sensors with UART interface

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypms)](https://pypi.org/project/pypms)
[![PyPI](https://img.shields.io/pypi/v/pypms)](https://pypi.org/project/pypms)
[![Build Status](https://github.com/avaldebe/PyPMS/actions/workflows/test.yml/badge.svg)](https://github.com/avaldebe/PyPMS/actions)
[![GitHub issues](https://img.shields.io/github/issues/avaldebe/PyPMS)](https://github.com/avaldebe/PyPMS/issues)
[![GitHub license](https://img.shields.io/github/license/avaldebe/PyPMS)](https://github.com/avaldebe/PyPMS/blob/master/LICENSE)
[![DOI](https://zenodo.org/badge/203110737.svg)](https://zenodo.org/badge/latestdoi/203110737)

[project site]: https://avaldebe.github.io/PyPMS

## Command Line Interface

``` man
Usage: pms [OPTIONS] COMMAND [ARGS]...

  Data acquisition and logging for Air Quality Sensors with UART interface

Options:
  -m, --sensor-model [HPMA115C0|HPMA115S0|MCU680|MHZ19B|PMS3003|PMS5003S|PMS5003ST|PMS5003T|PMSx003|SDS01x|SDS198|SPS30|ZH0xx]
                                  sensor model  [default: PMSx003]
  -s, --serial-port TEXT          serial port  [default: /dev/ttyUSB0]
  -i, --interval INTEGER          seconds to wait between updates  [default:
                                  60]

  -n, --samples INTEGER           stop after N samples
  --debug                         print DEBUG/logging messages  [default:
                                  False]

  -V, --version
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.

Commands:
  bridge    Bridge between MQTT and InfluxDB servers
  csv       Read sensor and print measurements
  influxdb  Read sensor and push PM measurements to an InfluxDB server
  info      Information about the sensor observations
  mqtt      Read sensor and push PM measurements to a MQTT server
  serial    Read sensor and print measurements
```

For details on a particular command and their options try `pms COMMAND --help`
or visit the [project site].

## Installation

```bash
# basic installation with pip
python3 -m pip install pypms

# or with pipx
pipx install pypms
```

Will allow you yo access to sensors via serial port (`pms serial`),
and save observations to a csv file (`pms csv`).

Additional packages are required for pushing observations to an mqtt server
(`pms mqtt`), to an influxdb server (`pms influxdb`), or provide a bridge
between mqtt and influxdb servers (`pms bridge`).

```bash
# full installation with pip
python3 -m pip install pypms[mqtt,influxdb]

# or with pipx
pipx install pypms[mqtt,influxdb]
```

For more details visit the [project site].

## Particulate Matter Sensors

| Sensor            | `--sensor-model` |  PM1  | PM2.5 |  PM4  | PM10  | size bins | Other                  | Tested |
| ----------------- | ---------------- | :---: | :---: | :---: | :---: | :-------: | ---------------------- | :----: |
| [Plantower]       |
| PMS1003 (aka G1)  | [PMSx003]        |   ✔️   |   ✔️   |       |   ✔️   |     6     |                        |        |
| PMS3003 (aka G3)  | [PMS3003]        |   ✔️   |   ✔️   |       |   ✔️   |           |                        |   ✔️    |
| PMS5003 (aka G5)  | [PMSx003]        |   ✔️   |   ✔️   |       |   ✔️   |     6     |                        |        |
| PMS5003T          | [PMS5003T]       |   ✔️   |   ✔️   |       |   ✔️   |     4     | temp. & rel.hum.       |        |
| PMS5003S          | [PMS5003S]       |   ✔️   |   ✔️   |       |   ✔️   |     6     | HCHO concentration     |        |
| PMS5003ST         | [PMS5003ST]      |   ✔️   |   ✔️   |       |   ✔️   |     6     | HCHO, temp. & rel.hum. |        |
| PMS7003 (aka G7)  | [PMSx003]        |   ✔️   |   ✔️   |       |   ✔️   |     6     |                        |   ✔️    |
| PMSA003 (aka G10) | [PMSx003]        |   ✔️   |   ✔️   |       |   ✔️   |     6     |                        |   ✔️    |
| [NovaFitness]     |
| SDS011            | [SDS01x]         |       |   ✔️   |       |   ✔️   |           |                        |   ✔️    |
| SDS018            | [SDS01x]         |       |   ✔️   |       |   ✔️   |           |                        |        |
| SDS021            | [SDS01x]         |       |   ✔️   |       |   ✔️   |           |                        |        |
| SDS198            | [SDS198]         |       |       |       |       |           | PM100                  |   ✔️    |
| [Honeywell]       |
| HPMA115S0         | [HPMA115S0]      |       |   ✔️   |       |   ✔️   |           |                        |        |
| HPMA115C0         | [HPMA115C0]      |   ✔️   |   ✔️   |   ✔️   |   ✔️   |           |                        |        |
| [Senserion]       |
| SPS30             | [SPS30]          |   ✔️   |   ✔️   |   ✔️   |   ✔️   |     5     | typical particle size  |        |
| [Winsen]          |
| ZH03B             | [ZH0xx]          |   ✔️   |   ✔️   |   ✔️   |       |           |                        |        |
| ZH06-I            | [ZH0xx]          |   ✔️   |   ✔️   |   ✔️   |       |           |                        |        |

[plantower]:  https://avaldebe.github.io/PyPMS/sensors/Plantower
[PMS3003]:    https://avaldebe.github.io/PyPMS/sensors/Plantower/#pms3003
[PMSx003]:    https://avaldebe.github.io/PyPMS/sensors/Plantower/#pmsx003
[PMS5003T]:   https://avaldebe.github.io/PyPMS/sensors/Plantower/#pms5003t
[PMS5003S]:   https://avaldebe.github.io/PyPMS/sensors/Plantower/#pms5003s
[PMS5003ST]:  https://avaldebe.github.io/PyPMS/sensors/Plantower/#pms5003st

[NovaFitness]:https://avaldebe.github.io/PyPMS/sensors/NovaFitness
[SDS01x]:     https://avaldebe.github.io/PyPMS/sensors/NovaFitness/#sds01x
[SDS198]:     https://avaldebe.github.io/PyPMS/sensors/NovaFitness/#sds198

[Honeywell]:  https://avaldebe.github.io/PyPMS/sensors/Honeywell
[HPMA115S0]:  https://avaldebe.github.io/PyPMS/sensors/Honeywell/#hpma115s0
[HPMA115C0]:  https://avaldebe.github.io/PyPMS/sensors/Honeywell/#hpma115c0

[Senserion]:  https://avaldebe.github.io/PyPMS/sensors/Senserion
[SPS30]:      https://avaldebe.github.io/PyPMS/sensors/Senserion/#sps30

[Winsen]:     https://avaldebe.github.io/PyPMS/sensors/Winsen
[ZH0xx]:      https://avaldebe.github.io/PyPMS/sensors/Winsen/#zh0xx
[MHZ19B]:     https://avaldebe.github.io/PyPMS/sensors/Winsen/#mhz19b

## Other Sensors

- [MCU680]:
  chinese module with a [BME680] sensor, a mirocontroller (μC) and 3.3V low-dropout regulator (LDO).
  The μC acts as I2C/UART bridge, providing outputs from the [closed source integration library][BSEC].
- [MHZ19B]:
  infrared CO2 sensor module from [Winsen].

[MCU680]:   https://avaldebe.github.io/PyPMS/sensors/mcu680/#mcu680
[BME680]:   https://avaldebe.github.io/PyPMS/sensors/mcu680/#bme680
[BSEC]:     https://www.bosch-sensortec.com/software-tools/software/bsec/

## Want More Sensors

For more Air Quality sensors [open an issue][issue].

[issue]: https://github.com/avaldebe/PyPMS/issues

## Use as a library

PyPMS/pms is meant as a command line application.
The [project site] contain some help for those brave enough to use its internals as a [library].

[library]: https://avaldebe.github.io/PyPMS/library_usage

## Changelog

- 0.6 WIP
  - [project site]
  - reorganize internal modules
    - `pms.core`: core functionality, such as `Sensor` and `SensorReader`
    - `pms.sensors`: sensor modules grouped by manufacturer
    - `pms.extra`: extra cli utilities, such as `pms influxdb` and `influxdb mqtt`
    - importing from `pms.sensor` is deprecated, import from `pms.core` instead
  - plugin architecture
    - load sensor modules from entry points advertized as `"pypms.sensors"`
    - load extra cli commands from entry points advertized as `"pypms.extras"`
  - support [Winsen] PM sensors and [MHZ19B] infrared CO2 sensor.
  - pm1/pm4/raw2_5/pm2_5 properties, [#17](https://github.com/avaldebe/PyPMS/issues/17)
- 0.5.0
  - set username/password with environment variables:
    - `$MQTT_USER` sets `--mqtt-user` on `pms mqtt` and `pms bridge`
    - `$MQTT_USER` sets `--mqtt-user` on `pms mqtt` and `pms bridge`
    - `$DB_USER` sets `--db-user` on `pms influxdb` and `pms bridge`
    - `$DB_PASS` sets `--db-pass` on `pms influxdb` and `pms bridge`
- 0.4.1
  - info about the sensor observations with `pms info`
  - fix [MCU680] obs.pres typo [#16](https://github.com/avaldebe/PyPMS/issues/16)
- 0.4.0
  - capture raw messages with `pms csv --capture`
  - decode captured messages with `pms serial --capture`
  - hexdump format with `pms serial --format hexdump`
  - deprecate subset observation method
- 0.3.1
  - fix influxdb default tags
- 0.3.0
  - option for a fix number of samples
  - PMSx003 consistency check after sleep/wake
- 0.2.*
  - widen project scope from PM sensors to AQ sensors in general
  - support [BME680] sensor ([MCU680] module)
- 0.1.*
  - widen project scope beyond [Plantower] PM sensors
  - support [NovaFitness], [Honeywell] and [Senserion] PM sensors
  - cli for logging to csv file, InfluxDB server or MQTT server
