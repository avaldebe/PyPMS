# PyPMS

Python application for PM sensors with serial interface

## Command line usage

```man
Read a PMS5003/PMS7003/PMSA003 sensor

Usage:
    pms <command> [<args>...]
    pms <command> --help
    pms --help

Commands:
    serial      print PM measurements
    mqtt        push PM measurements to a MQTT server
    influxdb    push PM measurements to an InfluxDB server
```

```man
Read a PMS5003/PMS7003/PMSA003 sensor and print PM measurements

Usage:
     pms serial [options]

Options:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    -f, --format <fmt>      (pm|num|csv)formatted output  [default: pm]
    --help                  display this help and exit

NOTE:
Environment variables take precedence over command line options
- PMS_INTERVAL      overrides -n, --interval
- PMS_SERIAL        overrides -s, --serial
- PMS_FORMAT        overrides -f, --format
```

```man
Read a PMS5003/PMS7003/PMSA003 sensor and push PM measurements to a MQTT server

Usage:
    pms mqtt [options]

Options:
    -t, --topic <topic>     MQTT root/topic [default: homie/test]
    -h, --host <host>       MQTT host server [default: test.mosquitto.org]
    -p, --port <port>       MQTT host port [default: 1883]
    -u, --user <username>   MQTT username
    -P, --pass <password>   MQTT password

Other:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --help                  display this help and exit

NOTE:
Environment variables take precedence over command line options
- PMS_MQTT_TOPIC    overrides -t, --topic
- PMS_MQTT_HOST     overrides -h, --host
- PMS_MQTT_PORT     overrides -p, --port
- PMS_MQTT_USER     overrides -u, --user
- PMS_MQTT_PASS     overrides -P, --pass
- PMS_INTERVAL      overrides -n, --interval
- PMS_SERIAL        overrides -s, --serial

NOTE:
Only partial support for Homie v2.0.0 MQTT convention
https://homieiot.github.io/specification/spec-core-v2_0_0/
```

```man
Read a PMS5003/PMS7003/PMSA003 sensor and push PM measurements to an InfluxDB server

Usage:
    pms influxdb [options]

Options:
    -d, --database <db>     InfluxDB database [default: homie]
    -t, --tags <dict>       InfluxDB measurement tags [default: {"location":"test"}]
    -h, --host <host>       InfluxDB host server [default: influxdb]
    -p, --port <port>       InfluxDB host port [default: 8086]
    -u, --user <username>   InfluxDB username [default: root]
    -P, --pass <password>   InfluxDB password [default: root]

Other:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --help                  display this help and exit

NOTE:
Environment variables take precedence over command line options
- PMS_INFLUX_DB     overrides -d, --database
- PMS_INFLUX_TAGS   overrides -t, --tags
- PMS_INFLUX_HOST   overrides -h, --host
- PMS_INFLUX_PORT   overrides -p, --port
- PMS_INFLUX_USER   overrides -u, --user
- PMS_INFLUX_PASS   overrides -P, --pass
- PMS_INTERVAL      overrides -n, --interval
- PMS_SERIAL        overrides -s, --serial
```
