# PyPMS

Python application for PM sensors with serial interface

## Command line interface

```man
Usage: pms [OPTIONS] COMMAND [ARGS]...

  Read PMSx003 sensor

Options:
  -m, --sensor-model TEXT  sensor model  [default: PMSx003]
  -s, --serial-port PATH   serial port  [default: /dev/ttyUSB0]
  -i, --interval INTEGER   seconds to wait between updates  [default: 60]
  --debug                  print DEBUG/logging messages
  --help                   Show this message and exit.

Commands:
  bridge    Bridge between MQTT and InfluxDB servers
  influxdb  Read sensor and push PM measurements to an InfluxDB server
  mqtt      Read sensor and push PM measurements to a MQTT server
  serial    Read sensor and print PM measurements
```

For details on a particular command and their options

```bash
pms COMMAND --help
```

### Tab completion

Commands:
  bridge    Bridge between MQTT and InfluxDB servers
  influxdb  Read sensor and push PM measurements to an InfluxDB server
  mqtt      Read sensor and push PM measurements to a MQTT server
  serial    Read sensor and print PM measurements

For details on a particular command and their options

```bash
pms COMMAND --help
```

## Sensors

| [Plantower][]     | Tested Works | Doesn't Work | Not Tested | Datasheet                     | Notes                |
| ----------------- | :----------: | :----------: | :--------: | ----------------------------- | -------------------- |
| PMS1003 (aka G1)  |              |              |     X      | [en][g1_aqmd],  [cn][g1_lcsc] |                      |
| PMS3003 (aka G3)  |              |              |     X      | [en][g3_aqmon], [cn][g3_lcsc] | No passive mode read |
| PMS5003 (aka G5)  |              |              |     X      | [en][g5_aqmd],  [cn][g5_lcsc] |                      |
| PMS7003 (aka G7)  |              |              |     X      | [cn][g7_lcsc]                 |                      |
| PMSA003 (aka G10) |      X       |              |            | [cn][gA_lcsc]                 |                      |

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
