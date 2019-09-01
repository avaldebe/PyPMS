# PyPMS

Python application for PM sensors with serial interface

## Command line usage

```man
Read a PMSx003 sensor and print PM measurements

Usage:
    python -m pms.serial [options]

Options:
    -s, --serial <port>     serial port [default: /ser/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    -f, --format <fmt>      (pm|num|csv)formatted output  [default: pm]
    --help                  display this help and exit
```

```man
Read a PMSx003 sensor and push PM measurements to a MQTT server

Usage:
    python -m pms.mqtt [options]

Options:
    -t, --topic <topic>     MQTT root/topic [default: homie/test]
    -h, --host <host>       MQTT host server [default: test.mosquitto.org]
    -p, --port <port>       MQTT host port [default: 1883]
    -u, --user <username>   MQTT username
    -P, --pass <password>   MQTT password

Other:
    -s, --serial <port>     serial port [default: /ser/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --help                  display this help and exit

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
    --help                  display this help and exit
```
