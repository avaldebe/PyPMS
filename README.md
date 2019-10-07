# PyPMS

Tools for reading PM sensors with serial (UART) interface, data acquisition and logging.

## Command line interface

```man
Usage: pms [OPTIONS] COMMAND [ARGS]...

  Read PMSx003 sensor

Options:
  -m, --sensor-model [PMSx003|PMS3003|SDS01x|SDS198|HPMA115S0|HPMA115C0|SPS30]
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

## Sensors

| Sensor            | `--sensor-model` |  PM1  | PM2.5 |  PM4  | PM10  | size bins | Other                 | Tested Works | Doesn't Work  | Not Tested | Datasheet                     | Notes                |
| ----------------- | ---------------- | :---: | :---: | :---: | :---: | :-------: | --------------------- | :----------: | :-----------: | :--------: | ----------------------------- | -------------------- |
| [Plantower][]     |
| PMS1003 (aka G1)  | `PMSx003`        |   X   |   X   |       |   X   |     6     |                       |              |               |     X      | [en][g1_aqmd],  [cn][g1_lcsc] |
| PMS3003 (aka G3)  | `PMS3003`        |       |   X   |       |   X   |           |                       |      X       |               |            | [en][g3_aqmon], [cn][g3_lcsc] | No passive mode read |
| PMS5003 (aka G5)  | `PMSx003`        |   X   |   X   |       |   X   |     6     |                       |              |               |     X      | [en][g5_aqmd],  [cn][g5_lcsc] |
| PMS5003T          |                  |   X   |   X   |       |   X   |     4     | temp. & rel.hum.      |              | not supported |
| PMS5003S          |                  |   X   |   X   |       |   X   |     6     | HCHO concentration    |              | not supported |
| PMS5003ST         |                  |   X   |   X   |       |   X   |     6     | HCHO, temp. & rel.hum.|              | not supported |
| PMS7003 (aka G7)  | `PMSx003`        |   X   |   X   |       |   X   |     6     |                       |      X       |               |            | [cn][g7_lcsc]                 |
| PMSA003 (aka G10) | `PMSx003`        |   X   |   X   |       |   X   |     6     |                       |      X       |               |            | [cn][gA_lcsc]                 |
| [NovaFitness][]   |
| SDS011            | `SDS01x`         |       |   X   |       |   X   |           |                       |      X       |               |            | [en][SDS011]                  |
| SDS018            | `SDS01x`         |       |   X   |       |   X   |           |                       |              |               |     X      | [en][SDS018]                  |
| SDS021            | `SDS01x`         |       |   X   |       |   X   |           |                       |              |               |     X      | [en][SDS021]                  |
| SDS198            | `SDS198`         |       |       |       |       |           | PM100                 |              |               |     X      | [en][SDS198]                  |
| [Honeywell][]     |
| HPMA115S0         | `HPMA115S0`      |       |   X   |       |   X   |           |                       |              |               |     X      | [en][HPMA115]                 |
| HPMA115C0         | `HPMA115C0`      |   X   |   X   |   X   |   X   |           |                       |              |               |     X      | [en][HPMA115]                 |
| [Senserion][]     |
| SPS30             | `SPS30`          |   X   |   X   |   X   |   X   |     5     | typical particle size |              |               |     X      | [en][SPS30]                   | UART 115200 8N1      |

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

[NovaFitness]: http://inovafitness.com/en/a/index.html
[SDS011]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS011%20laser%20PM2.5%20sensor%20specification-V1.3.pdf
[SDS018]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS018%20Laser%20PM2.5%20Product%20Spec%20V1.5.pdf
[SDS021]: https://cdn.sparkfun.com/assets/parts/1/2/2/7/5/SDS021_laser_PM2.5_sensor_specification-V1.0.pdf
[SDS198]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS198%20laser%20PM100%20sensor%20specification-V1.2.pdf

[Honeywell]: https://sensing.honeywell.com/sensors/particle-sensors/hpm-series
[HPMA115]: https://sensing.honeywell.com/honeywell-sensing-particulate-hpm-series-datasheet-32322550

[Senserion]: https://www.sensirion.com/en/environmental-sensors/particulate-matter-sensors-pm25/
[SPS30]: https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Particulate_Matter/Sensirion_PM_Sensors_SPS30_Datasheet.pdf
