# Serial Air Quality Sensors

Data acquisition and logging for Air Quality Sensors with UART interface

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypms)](https://pypi.org/project/pypms)
[![PyPI](https://img.shields.io/pypi/v/pypms)](https://pypi.org/project/pypms)
[![Build Status](https://github.com/avaldebe/PyPMS/actions/workflows/test.yml/badge.svg)](https://github.com/avaldebe/PyPMS/actions)
[![GitHub issues](https://img.shields.io/github/issues/avaldebe/PyPMS)](https://github.com/avaldebe/PyPMS/issues)
[![GitHub license](https://img.shields.io/github/license/avaldebe/PyPMS)](https://github.com/avaldebe/PyPMS/blob/master/LICENSE)
[![DOI](https://zenodo.org/badge/203110737.svg)](https://zenodo.org/badge/latestdoi/203110737)

[project site]: https://avaldebe.github.io/PyPMS

## Installation

This package can be pip installed.
Please visit [project site] for detailed instructions.

## Command Line Tools

This package provides tools for requesting new measurements from the sensors
and print them on different formats, save them to a CSV file,
or push them to an external service such as an MQTT or InfluxDB server.
MQTT or InfluxDB server support requires additional packages.
Please visit [project site] for details.

## Particulate Matter Sensors

| Sensor            | `--sensor-model` |  PM1  | PM2.5 |  PM4  | PM10  | size bins | Other                  | Tested |
| ----------------- | ---------------- | :---: | :---: | :---: | :---: | :-------: | ---------------------- | :----: |
| [Plantower]       |
| PMS1003 (aka G1)  | [PMSx003]        |   ✔️   |   ✔️   |       |   ✔️   |     6     |                        |        |
| PMS3003 (aka G3)  | [PMS3003]        |   ✔️   |   ✔️   |       |   ✔️   |           |                        |   ✔️    |
| PMS5003 (aka G5)  | [PMSx003]        |   ✔️   |   ✔️   |       |   ✔️   |     6     |                        |        |
| PMS5003T          | [PMS5003T]       |   ✔️   |   ✔️   |       |   ✔️   |     4     | temp. & rel.hum.       |   ✔️    |
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
| HPMA115C0         | [HPMA115C0]      |   ✔️   |   ✔️   |   ✔️   |   ✔️   |           |                        |   ✔️    |
| [Sensirion]       |
| SPS30             | [SPS30]          |   ✔️   |   ✔️   |   ✔️   |   ✔️   |     5     | typical particle size  |   ✔️    |
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

[Sensirion]:  https://avaldebe.github.io/PyPMS/sensors/Sensirion
[SPS30]:      https://avaldebe.github.io/PyPMS/sensors/Sensirion/#sps30

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

- 0.8.0
  - add Python 3.12 and 3.13 support, drop Python 3.8 support
  - require typer-slim instead of full typer
  - require (optional) paho-mqtt v2+
  - tidy up annotations
- 0.7.1
  - disable logging unless CLI is running [PR#37](https://github.com/avaldebe/PyPMS/pull/37)
- 0.7.0
  - add Python 3.11 support and drop Python 3.7 support
  - pre-heat for PMSx003 sensors [PR#35](https://github.com/avaldebe/PyPMS/pull/35)
  - `open`/`close` methods for granular SensorReader operation [PR#33](https://github.com/avaldebe/PyPMS/pull/33)
  - fix HPMA115C0 header [#26](https://github.com/avaldebe/PyPMS/issues/26)
- 0.6.2
  - move logger config to CLI module [PR#28](https://github.com/avaldebe/PyPMS/pull/28)
- 0.6.1
  - fix `pms.sensors.sensirion` module name and docs
  - reliably recognize SPS30 sensor [#25](https://github.com/avaldebe/PyPMS/issues/25)
- 0.6.0
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
  - support [NovaFitness], [Honeywell] and [Sensirion] PM sensors
  - cli for logging to csv file, InfluxDB server or MQTT server
