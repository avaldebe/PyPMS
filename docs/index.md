# Getting started

## About

`pms` is a data acquisition and logging tool for for Air Quality Sensors with UART interface.

## Installation

=== "pip"

    ``` bash
    python3 -m pip install pypms
    ```

=== "pipx"

    ``` bash
    pipx install pypms
    ```

=== "uv tool"

    ``` bash
    uv tool install pypms
    ```

Will allow you yo access to sensors via serial port (`pms serial`),
and save observations to a csv file (`pms csv`).

### Install with extras

Additional packages are required for pushing observations to an mqtt server
(`pms mqtt`), to an influxdb server (`pms influxdb`), or provide a bridge
between mqtt and influxdb servers (`pms bridge`).

=== "pip"

    ``` bash
    python3 -m pip install pypms[mqtt,influxdb]
    ```

=== "pipx"

    ``` bash
    pipx install pypms[mqtt,influxdb]
    ```

=== "uv tool"

    ``` bash
    uv tool install pypms[mqtt,influxdb]
    ```

## Command line options

=== "pms"

    ``` bash
    pms --help
    ```

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

=== "pms info"

    ``` bash
    pms info --help
    ```

    ``` man
    Usage: pms info [OPTIONS]

      Information about the sensor observations

    Options:
      --help  Show this message and exit.
    ```

=== "pms serial"

    ``` bash
    pms serial --help
    ```

    ``` man
    Usage: pms serial [OPTIONS]

      Read sensor and print formatted measurements

    Options:
      -f, --format [csv|pm|num|raw|cf|atm|hcho|co2|bme|bsec|hexdump]
                                      formatted output
      --decode PATH                   decode captured messages
      --help                          Show this message and exit.
    ```

=== "pms csv"

    ``` bash
    pms csv --help
    ```

    ``` man
    Usage: pms csv [OPTIONS] [PATH]

      Read sensor and save measurements to a CSV file

    Arguments:
      [PATH]  csv formatted file

    Options:
      --capture    write raw messages instead of observations  [default: False]
      --overwrite  overwrite file, if already exists  [default: False]
      --help       Show this message and exit.
    ```

=== "pms mqtt"

    ``` bash
    pms mqtt --help
    ```

    ``` man
    Usage: pms mqtt [OPTIONS]

      Read sensor and push PM measurements to a MQTT server

    Options:
      -t, --topic TEXT     mqtt root/topic  [default: homie/test]
      --mqtt-host TEXT     mqtt server  [default: mqtt.eclipse.org]
      --mqtt-port INTEGER  server port  [default: 1883]
      --mqtt-user TEXT     server username  [env var: MQTT_USER]
      --mqtt-pass TEXT     server password  [env var: MQTT_PASS]
      --help               Show this message and exit.
    ```

=== "pms influxdb"

    ``` bash
    pms influxdb --help
    ```

    ``` man
    Usage: pms influxdb [OPTIONS]

      Read sensor and push PM measurements to an InfluxDB server

    Options:
      --db-host TEXT     database server  [default: influxdb]
      --db-port INTEGER  server port  [default: 8086]
      --db-user TEXT     server username  [env var: DB_USER; default: root]
      --db-pass TEXT     server password  [env var: DB_PASS; default: root]
      --db-name TEXT     database name  [default: homie]
      --tags TEXT        measurement tags  [default: {"location": "test"}]
      --help             Show this message and exit.
    ```

=== "pms bridge"

    ``` bash
    pms bridge --help
    ```

    ``` man
    Usage: pms bridge [OPTIONS]

      Bridge between MQTT and InfluxDB servers

    Options:
      --mqtt-topic TEXT    mqtt root/topic  [default: homie/+/+/+]
      --mqtt-host TEXT     mqtt server  [default: mqtt.eclipse.org]
      --mqtt-port INTEGER  server port  [default: 1883]
      --mqtt-user TEXT     server username  [env var: MQTT_USER]
      --mqtt-pass TEXT     server password  [env var: MQTT_PASS]
      --db-host TEXT       database server  [default: influxdb]
      --db-port INTEGER    server port  [default: 8086]
      --db-user TEXT       server username  [env var: DB_USER; default: root]
      --db-pass TEXT       server password  [env var: DB_PASS; default: root]
      --db-name TEXT       database name  [default: homie]
      --help               Show this message and exit.
    ```
