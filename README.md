# PyPMS

Python application for PM sensors with serial interface

## Command line usage

```man
Read a PMSx003 sensor and print PM measurements

Usage:
    python -m pms [options]

Options:
    -s, --serial <port>     serial port [default: /ser/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --csv                   csv formatted output
    -h, --help              display this help and exit
```

```man
Read a PMSx003 sensor and push PM measurements to a MQTT server

Usage:
    python -m pms.mqtt [options]

Options:
    --topic <topic>         MQTT topic [default: homie/test]
    --host <host>           MQTT host server [default: test.mosquitto.org]
    --port <port>           MQTT host port [default: 1883]
    --user <username>       MQTT username
    --pass <password>       MQTT password

Other:
    -s, --serial <port>     serial port [default: /ser/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    -h, --help              display this help and exit

Notes:
- Only partial support for Homie v2.0.0 MQTT convention 
  https://homieiot.github.io/specification/spec-core-v2_0_0/
```

```man
Read PMSx003 sensor and push PM measurements to an InfluxDB server

Usage:
    python -m pms.influxdb [options]

Options:
    --location <tag>        InfluxDB location tag [default: test]
    --database <db>         InfluxDB database [default: homie]
    --host <host>           InfluxDB host server [default: influxdb]
    --port <port>           InfluxDB host port [default: 8086]
    --user <username>       InfluxDB username [default: root]
    --pass <password>       InfluxDB password [default: root]

Other:
    -s, --serial <port>     serial port [default: /ser/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    -h, --help              display this help and exit
```
