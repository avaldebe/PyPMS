# [Plantower] sensors

!!! warning
    This sensors are 3.3V devices. They require 5V power to operate the laser and fan.
    However, the I/O pins are not 5V tolerant and the sensor will be damaged by 5V logic.

=== "sensor"

    | Sensor    | `--sensor-model` |       PM1        |      PM2.5       |       PM10       | size bins | Other                  |
    | --------- | ---------------- | :--------------: | :--------------: | :--------------: | :-------: | ---------------------- |
    | PMS1003   | [PMSx003]        | :material-check: | :material-check: | :material-check: |     6     |                        |
    | PMS3003   | [PMS3003]        | :material-check: | :material-check: | :material-check: |           | No passive mode read   |
    | PMS5003   | [PMSx003]        | :material-check: | :material-check: | :material-check: |     6     |                        |
    | PMS5003T  | [PMS5003T]       | :material-check: | :material-check: | :material-check: |     4     | temp. & rel.hum.       |
    | PMS5003S  | [PMS5003S]       | :material-check: | :material-check: | :material-check: |     6     | HCHO concentration     |
    | PMS5003ST | [PMS5003ST]      | :material-check: | :material-check: | :material-check: |     6     | HCHO, temp. & rel.hum. |
    | PMS7003   | [PMSx003]        | :material-check: | :material-check: | :material-check: |     6     |                        |
    | PMSA003   | [PMSx003]        | :material-check: | :material-check: | :material-check: |     6     |                        |

=== "datasheet"

    | Sensor    | Datasheet                     | Dimensions   | Connector            |
    | --------- | ----------------------------- | ------------ | -------------------- |
    | PMS1003   | [en][g1_aqmd],  [cn][g1_lcsc] | 42x65x23 mm³ | [8 pin](#connector)  |
    | PMS3003   | [en][g3_aqmon], [cn][g3_lcsc] | 43x50x21 mm³ | [8 pin](#connector)  |
    | PMS5003   | [en][g5_aqmd],  [cn][g5_lcsc] | 38x50x21 mm³ | [8 pin](#connector)  |
    | PMS5003T  |                               | 38x50x21 mm³ | [8 pin](#connector)  |
    | PMS5003S  |                               | 38x50x21 mm³ | [8 pin](#connector)  |
    | PMS5003ST |                               | 38x50x21 mm³ | [8 pin](#connector)  |
    | PMS7003   | [cn][g7_lcsc]                 | 37x48x12 mm³ | [10 pin](#connector) |
    | PMSA003   | [cn][gA_lcsc]                 |              | [10 pin](#connector) |

[plantower]:  http://www.plantower.com/
[g1_aqmd]:    http://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms1003-manual_v2-5.pdf?sfvrsn=2
[g5_aqmd]:    http://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms5003-manual_v2-3.pdf?sfvrsn=2
[g3_aqmon]:   https://github.com/avaldebe/AQmon/raw/master/Documents/PMS3003_LOGOELE.pdf
[g5_aqmon]:   https://github.com/avaldebe/AQmon/raw/master/Documents/PMS5003_LOGOELE.pdf
[g1_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMS1003_C89289.pdf
[g3_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMS3003_C87024.pdf
[g5_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMS5003_C91431.pdf
[g7_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMS7003_C84815.pdf
[gA_lcsc]:    https://datasheet.lcsc.com/szlcsc/PMSA003-A_C132744.pdf

[PMSx003]:    #pmsx003
[PMS3003]:    #pms3003
[PMS5003T]:   #pms5003t
[PMS5003S]:   #pms5003s
[PMS5003ST]:  #pms5003st

## Connector

=== "8 pin"

    8 pin Molex 1.25mm "PicoBlade" 51021 compatible, found online as 1.25mm JST.

    | Pin | Name  | Voltage  | Function                      |
    | --- | ----- | -------- | ----------------------------- |
    | 1   | VCC   | 5V       |
    | 2   | GND   | 0V       |
    | 3   | SET   | 3.3V TTL | wake (hight)/sleep (low) mode |
    | 4   | RX    | 3.3V TTL | serial port                   |
    | 5   | TX    | 3.3V TTL | serial port                   |
    | 6   | RESET | 3,3V TTL | reset (low)                   |
    | 7/8 | NC    |          | not connected                 |

=== "10 pin"

    5x2 1.27mm female header

    | Pin | Name  | Voltage  | Function                      |
    | --- | ----- | -------- | ----------------------------- |
    | 1/2 | VCC   | 5V       |
    | 3/4 | GND   | 0V       |
    | 5   | RESET | 3,3V TTL | reset (low)                   |
    | 6   | NC    |          | not connected                 |
    | 7   | RX    | 3.3V TTL | serial port                   |
    | 8   | NC    |          | not connected                 |
    | 9   | TX    | 3.3V TTL | serial port                   |
    | 10  | SET   | 3.3V TTL | wake (hight)/sleep (low) mode |

## Protocol

Serial protocol is UART 9600 8N1 :material-alert: 3.3V TTL.

=== "commands"

    With the exception of the [PMS3003], all the Plantower PM sensors
    can be fully controlled with serial commands:

    | Command        | Description                     | `message`              |
    | -------------- | ------------------------------- | ---------------------- |
    | `active_mode`  | continuous operation            | `42 4D E1 00 01 01 71` |
    | `passive_mode` | single-shot operation           | `42 4D E1 00 00 01 70` |
    | `passive_read` | trigger single-shot measurement | `42 4D E2 00 00 01 71` |
    | `sleep`        | sleep mode                      | `42 4D E4 00 00 01 73` |
    | `wake`         | wake up from sleep mode         | `42 4D E4 00 01 01 74` |

=== "message"

    Messages containing measurements consist of unsigned short integers.
    The last 2 bits of the message should contain `sum(message[:2])`.

    | `message` | [PMS3003]            | [PMSx003]             | [PMS5003T]    | [PMS5003S]    | [PMS5003ST]           |
    | --------- | -------------------- | --------------------- | ------------- | ------------- | --------------------- |
    |           | 24 bits              | 32 bits               | 32 bits       | 32 bits       | 40 bits               |
    | header    | 4 bits               | 4 bits                | 4 bits        | 4 bits        | 4 bits                |
    |           | `42 4d 00 14`        | `42 4d 00 1c`         | `42 4d 00 1c` | `42 4d 00 1c` | `42 4d 00 24`         |
    | body      | 18 bits              | 26 bits               | 26 bits       | 26 bits       | 34 bits               |
    |           | 6 values, 3 reserved | 12 values, 1 reserved | 13 values     | 13 values     | 15 values, 2 reserved |
    | checksum  | 2 bits               | 2 bits                | 2 bits        | 2 bits        | 2 bits                |

=== "PMS3003"

    The message body (`message[4:16]`) contains 6 values:

    - raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
    - pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]

=== "PMSx003"

    The message body (`message[4:28]`) contains 12 values:

    - raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
    - pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]
    - n0_3, n0_5, n1_0, n2_5, n5_0, n10_0: number of particles under X_Y μm [#/cm³] (raw values [#/100 cm³])

=== "PMS5003T"

    The message body (`message[4:28]`) contains 12 values:

    - raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
    - pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]
    - n0_3, n0_5, n1_0, n2_5: number of particles under X_Y um [#/cm³] (raw values [#/100 cm³])
    - temp: temperature [°C]
    - rhum: relative humidity [%]

=== "PMS5003S"

    The message body (`message[4:30]`) contains 13 values:

    - raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
    - pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]
    - n0_3, n0_5, n1_0, n2_5, n5_0, n10_0: number of particles under X_Y um [#/cm³] (raw values [#/100 cm³])
    - HCHO: concentration of formaldehyde [μg/m³]

=== "PMS5003ST"

    The message body (`message[4:34]`) contains 15 values:

    - raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
    - pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]
    - n0_3, n0_5, n1_0, n2_5, n5_0, n10_0: number of particles under X_Y um [#/cm³] (raw values [#/100 cm³])
    - HCHO: concentration of formaldehyde [μg/m³]
    - temp: temperature [°C]
    - rhum: relative humidity [%]

## PMS3003

!!! note
    This sensors does not support passive mode sampling

=== "info"

    About the PMS3003 sensor (`-m PMS3003`)

    ``` bash
    pms -m PMS3003 info
    ```

    ``` man
    --8<-- "PMS3003.info"
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMS3003 -n 10 -i 10 serial
    ```

    ``` csv
    --8<-- "PMS3003.txt"
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMS3003 -n 10 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "PMS3003.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMS3003 -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "PMS3003.hexdump"
    ```

## PMSx003

=== "info"

    About the sensors supported by the PMSx003 protocol (`-m PMSx003`)

    ``` bash
    pms -m PMSx003 info
    ```

    ``` man
    --8<-- "PMSx003.info"
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMSx003 -n 10 -i 10 serial
    ```

    ``` csv
    --8<-- "PMSx003.txt"
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMSx003 -n 10 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "PMSx003.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMSx003 -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "PMSx003.hexdump"
    ```

## PMS5003T

=== "info"

    About the PMS5003T sensor (`-m PMS5003T`)

    ``` bash
    pms -m PMS5003T info
    ```

    ``` man
    --8<-- "PMS5003T.info"
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMS5003T -n 10 -i 10 serial
    ```

    ``` csv
    --8<-- "PMS5003T.txt"
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMS5003T -n 10 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "PMS5003T.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMS5003T -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "PMS5003T.hexdump"
    ```

## PMS5003S

=== "info"

    About the PMS5003S sensor (`-m PMS5003S`)

    ``` bash
    pms -m PMS5003S info
    ```

    ``` man
    --8<-- "PMS5003S.info"
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMS5003S -n 10 -i 10 serial
    ```

    ``` csv
    --8<-- "PMS5003S.txt"
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMS5003S -n 10 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "PMS5003S.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMS5003S -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "PMS5003S.hexdump"
    ```

## PMS5003ST

=== "info"

    About the PMS5003ST sensor (`-m PMS5003ST`)

    ``` bash
    pms -m PMS5003ST info
    ```

    ``` man
    --8<-- "PMS5003ST.info"
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMS5003ST -n 10 -i 10 serial
    ```

    ``` csv
    --8<-- "PMS5003ST.txt"
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMS5003ST -n 10 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "PMS5003ST.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMS5003ST -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "PMS5003ST.hexdump"
    ```
