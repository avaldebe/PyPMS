# PyPMS

Tools for reading PM sensors with serial interface, data acquisition and logging.

## Command line interface

```man
Usage: pms [OPTIONS] COMMAND [ARGS]...

  Read PMSx003 sensor

Options:
  -m, --sensor-model [PMSx003|PMS3003|SDS01x]
                                  sensor model  [default: PMSx003]
  -s, --serial-port PATH          serial port  [default: /dev/ttyUSB0]
  -i, --interval INTEGER          seconds to wait between updates  [default:
                                  60]
  --debug                         print DEBUG/logging messages
  --help                          Show this message and exit.

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

| [Plantower][]     | Tested Works | Doesn't Work | Not Tested | Datasheet                     | Notes                 |
| ----------------- | :----------: | :----------: | :--------: | ----------------------------- | --------------------- |
| PMS1003 (aka G1)  |              |              |     X      | [en][g1_aqmd],  [cn][g1_lcsc] | Include number counts |
| PMS3003 (aka G3)  |              |              |     X      | [en][g3_aqmon], [cn][g3_lcsc] | No passive mode read  |
| PMS5003 (aka G5)  |              |              |     X      | [en][g5_aqmd],  [cn][g5_lcsc] | Include number counts |
| PMS7003 (aka G7)  |              |              |     X      | [cn][g7_lcsc]                 | Include number counts |
| PMSA003 (aka G10) |      X       |              |            | [cn][gA_lcsc]                 | Include number counts |

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

| [NovaFitness][] | Tested Works | Doesn't Work  | Not Tested | Datasheet    | Notes               |
| --------------- | :----------: | :-----------: | :--------: | ------------ | ------------------- |
| SDS011          |              |               |     X      | [en][SDS011] | only PM2.5 and PM10 |
| SDS018          |              |               |     X      | [en][SDS018] | only PM2.5 and PM10 |
| SDS198          |              | Not supported |            | [en][SDS198] | only PM100          |

[NovaFitness]: http://inovafitness.com/en/a/index.html
[SDS011]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS011%20laser%20PM2.5%20sensor%20specification-V1.3.pdf
[SDS018]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS018%20Laser%20PM2.5%20Product%20Spec%20V1.5.pdf
[SDS198]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS198%20laser%20PM100%20sensor%20specification-V1.2.pdf
