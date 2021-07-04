# Getting started

## About

`pms` is a data acquisition and logging tool for for Air Quality Sensors with UART interface.

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

## Usage

```man
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

For details on a particular command and their options

```bash
pms COMMAND --help
```
