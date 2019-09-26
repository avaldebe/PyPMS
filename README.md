# PyPMS

Python application for PM sensors with serial interface

## Sensors

| [Plantower][]     | Tested Works | Doesn't Work | Not Tested | Datasheet                     | Notes                |
| ----------------- | :----------: | :----------: | :--------: | ----------------------------- | -------------------- |
| PMS1003 (aka G1)  |              |              |     X      | [en][g1_aqmd],  [cn][g1_lcsc] |
| PMS3003 (aka G3)  |              |              |     X      | [en][g3_aqmon], [cn][g3_lcsc] | No passive mode read |
| PMS5003 (aka G5)  |              |              |     X      | [en][g5_aqmd],  [cn][g5_lcsc] |
| PMS7003 (aka G7)  |              |              |     X      | [cn][g7_lcsc]                 |
| PMSA003 (aka G10) |      X       |              |            | [cn][gA_lcsc]                 |

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

The command line utility is build using [invoke][], so we can use the [tab-completion][]
as follows:

[invoke]: https://www.pyinvoke.org/
[tab-completion]: http://docs.pyinvoke.org/en/latest/invoke.html#tab-completion

```bash
source <(pms --print-completion-script bash)
```

```man
Usage: pms [--core-opts] <subcommand> [--subcommand-opts] ...

Core options:
  ... core options here, minus task-related ones ...
  
Subcommands:

  bridge     Bridge between MQTT server/topic and InfluxDB server/database
  influxdb   Read PMSx003 sensor and push PM measurements to an InfluxDB server
  mqtt       Read PMSx003 sensor and push PM measurements to a MQTT server
  serial     Read PMSx003 sensor and print PM measurements
```

```man
Usage: pms [--core-opts] serial [--options] [other tasks here ...]

Docstring:
  Read PMSx003 sensor and print PM measurements

Options:
  -d, --debug                  print DEBUG/logging messages
  -f STRING, --format=STRING   (pm|num|csv)formatted output  [default: pm]
  -i INT, --interval=INT       seconds to wait between updates [default: 60]
  -s STRING, --serial=STRING   serial port [default: /dev/ttyUSB0]```

```man
Usage: pms [--core-opts] mqtt [--options] [other tasks here ...]

Docstring:
  Read PMSx003 sensor and push PM measurements to a MQTT server

Options:
  --=STRING, --mqtt-user=STRING   server username
  -d, --debug                     print DEBUG/logging messages
  -i INT, --interval=INT          seconds to wait between updates [default: 60]
  -m STRING, --mqtt-host=STRING   mqtt server [default: mqtt.eclipse.org]
  -p STRING, --mqtt-pass=STRING   server password
  -q INT, --mqtt-port=INT         server port [default: 1883]
  -s STRING, --serial=STRING      serial port [default: /dev/ttyUSB0]
  -t STRING, --topic=STRING       mqtt root/topic [default: homie/test]
```

```man
Usage: pms [--core-opts] influxdb [--options] [other tasks here ...]

Docstring:
  Read PMSx003 sensor and push PM measurements to an InfluxDB server

Options:
  --=STRING, --db-user=STRING   server username [default: root]
  -b INT, --db-port=INT         server port [default: 8086]
  -d STRING, --db-host=STRING   database server [default: influxdb]
  -e, --debug                   print DEBUG/logging messages
  -i INT, --interval=INT        seconds to wait between updates [default: 60]
  -n STRING, --db-name=STRING   database name [default: homie]
  -p STRING, --db-pass=STRING   server password [default: root]
  -s STRING, --serial=STRING    serial port [default: /dev/ttyUSB0]
  -t STRING, --tags=STRING      measurement tags [default: {'location':'test'}]
```

```man
Usage: pms [--core-opts] bridge [--options] [other tasks here ...]

Docstring:
  Bridge between MQTT server/topic and InfluxDB server/database

Options:
  --=STRING, --mqtt-pass=STRING   server password
  -b INT, --db-port=INT           server port [default: 8086]
  -d STRING, --db-host=STRING     database server [default: influxdb]
  -e, --debug                     print DEBUG/logging messages
  -m STRING, --mqtt-host=STRING   mqtt server [default: mqtt.eclipse.org]
  -n STRING, --db-name=STRING     database name [default: homie]
  -p STRING, --db-pass=STRING     server password [default: root]
  -q INT, --mqtt-port=INT         server port [default: 1883]
  -t STRING, --mqtt-user=STRING   server username
  -u STRING, --db-user=STRING     server username [default: root]
```
