# PyPMS

Python application for PM sensors with serial interface

## Sensors

[Plantower][]      | Tested Works | Doesn't Work | Not Tested  | Datasheet | Notes
------------------ | :----------: | :----------: | :---------: | --------- | -----
PMS1003 (aka G1)   |    |   | X | [en][g1_aqmd],  [cn][g1_lcsc] |
PMS3003 (aka G3)   |    |   | X | [en][g3_aqmon], [cn][g3_lcsc] | No passive mode read
PMS5003 (aka G5)   |    |   | X | [en][g5_aqmd],  [cn][g5_lcsc] |
PMS7003 (aka G7)   |    |   | X |                 [cn][g7_lcsc] |
PMSA003 (aka G10)  |  X |   |   |                 [cn][gA_lcsc] |

[plantower]: http://www.plantower.com/
[g1_aqmd]:    http://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms1003-manual_v2-5.pdf?sfvrsn=2
[g5_aqmd]:    http://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms5003-manual_v2-3.pdf?sfvrsn=2
[g3_aqmon]:   https://github.com/avaldebe/AQmon/raw/master/Documents/PMS3003_LOGOELE.pdf
[g5_aqmon]:   https://github.com/avaldebe/AQmon/raw/master/Documents/PMS5003_LOGOELE.pdf
[g1_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMS1003_C89289.pdf
[g3_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMS3003_C87024.pdf
[g5_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMS5003_C91431.pdf
[g7_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMS7003_C84815.pdf
[gA_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMSA003-A_C132744.pdf

## Command line usage

```man
Read a PMSx003 sensor

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
Read a PMSx003 sensor and print PM measurements

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
Read a PMSx003 sensor and push PM measurements to a MQTT server

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
