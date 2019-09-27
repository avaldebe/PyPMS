# PyPMS

Python application for PM sensors with serial interface

## Command line interface

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

For details on the subcommands and subcommand options

```bash
pms --help <subcommand>
```

### Tab completion

The command line utility is build around [invoke][], so we can setup [tab completion][] as follows:

[invoke]: https://www.pyinvoke.org/
[tab completion]: http://docs.pyinvoke.org/en/latest/invoke.html#tab-completion

```bash
# bash completion
source <(pms --print-completion-script bash)
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
