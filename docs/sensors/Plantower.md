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
    Plantower PMS3003 sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]

    String formats: pm (default), raw, cf, csv and header
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMS3003 -n 10 -i 10 serial
    ```

    ``` csv
    2020-09-27 17:16:10: PM1 0.0, PM2.5 0.0, PM10 0.0 μg/m3
    2020-09-27 17:16:20: PM1 0.0, PM2.5 0.0, PM10 0.0 μg/m3
    2020-09-27 17:16:30: PM1 0.0, PM2.5 0.0, PM10 0.0 μg/m3
    2020-09-27 17:16:40: PM1 0.0, PM2.5 0.0, PM10 0.0 μg/m3
    2020-09-27 17:16:50: PM1 1.0, PM2.5 1.0, PM10 1.0 μg/m3
    2020-09-27 17:17:00: PM1 1.0, PM2.5 1.0, PM10 1.0 μg/m3
    2020-09-27 17:17:10: PM1 1.0, PM2.5 1.0, PM10 1.0 μg/m3
    2020-09-27 17:17:20: PM1 0.0, PM2.5 0.0, PM10 0.0 μg/m3
    2020-09-27 17:17:30: PM1 0.0, PM2.5 0.0, PM10 0.0 μg/m3
    2020-09-27 17:17:40: PM1 0.0, PM2.5 0.0, PM10 0.0 μg/m3    
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMS3003 -n 10 -i 10 serial -f csv
    ```

    ``` csv
    time, raw01, raw25, raw10, pm01, pm25, pm10, n0_3, n0_5, n1_0, n2_5, temp, rhum
    1612247287, 21, 36, 36, 20.0, 33.0, 36.0, 35.28, 10.55, 2.28, 0.14, 21.2, 22.4
    1612247297, 21, 37, 38, 20.0, 34.0, 38.0, 38.40, 11.26, 2.50, 0.22, 21.2, 22.4
    1612247307, 20, 35, 42, 19.0, 32.0, 42.0, 37.50, 10.79, 2.62, 0.30, 21.2, 22.3
    1612247317, 23, 38, 38, 22.0, 35.0, 38.0, 38.16, 11.22, 2.86, 0.14, 21.2, 22.4
    1612247327, 22, 37, 39, 21.0, 34.0, 39.0, 38.37, 11.14, 2.88, 0.20, 21.2, 22.3
    1612247337, 22, 36, 42, 21.0, 33.0, 42.0, 37.59, 11.10, 2.82, 0.22, 21.2, 22.3
    1612247347, 23, 37, 45, 22.0, 34.0, 45.0, 38.37, 11.35, 2.92, 0.22, 21.3, 22.2
    1612247357, 21, 35, 44, 20.0, 32.0, 44.0, 37.86, 11.14, 2.86, 0.24, 21.3, 22.2
    1612247367, 20, 34, 43, 19.0, 32.0, 43.0, 36.03, 10.44, 2.72, 0.30, 21.3, 22.3
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMS3003 -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    00000000: 42 4d 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 51 00 f4  BM...................Q..
    00000018: 42 4d 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 51 00 f4  BM...................Q..
    00000030: 42 4d 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 51 00 f4  BM...................Q..
    00000048: 42 4d 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 51 00 f4  BM...................Q..
    00000060: 42 4d 00 14 00 01 00 01 00 01 00 01 00 01 00 01 00 00 00 00 00 51 00 fa  BM...................Q..
    00000078: 42 4d 00 14 00 01 00 01 00 01 00 01 00 01 00 01 00 00 00 00 00 51 00 fa  BM...................Q..
    00000090: 42 4d 00 14 00 01 00 01 00 01 00 01 00 01 00 01 00 00 00 00 00 51 00 fa  BM...................Q..
    000000a8: 42 4d 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 51 00 f4  BM...................Q..
    000000c0: 42 4d 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 51 00 f4  BM...................Q..
    000000d8: 42 4d 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 51 00 f4  BM...................Q..
    ```

## PMSx003

=== "info"

    About the sensors supported by the PMSx003 protocol (`-m PMSx003`)

    ``` bash
    pms -m PMSx003 info
    ```

    ``` man
    Plantower PMS1003, PMS5003, PMS7003 and PMSA003 sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations over X.Y um [#/cm3]

    String formats: pm (default), raw, cf, num, csv and header
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMSx003 -n 10 -i 10 serial
    ```

    ``` csv
    2020-09-27 17:16:10: PM1 0.0, PM2.5 8.0, PM10 8.0 μg/m3
    2020-09-27 17:16:20: PM1 0.0, PM2.5 7.0, PM10 7.0 μg/m3
    2020-09-27 17:16:30: PM1 0.0, PM2.5 7.0, PM10 7.0 μg/m3
    2020-09-27 17:16:40: PM1 0.0, PM2.5 7.0, PM10 7.0 μg/m3
    2020-09-27 17:16:50: PM1 0.0, PM2.5 7.0, PM10 7.0 μg/m3
    2020-09-27 17:17:00: PM1 0.0, PM2.5 6.0, PM10 6.0 μg/m3
    2020-09-27 17:17:10: PM1 0.0, PM2.5 6.0, PM10 6.0 μg/m3
    2020-09-27 17:17:20: PM1 0.0, PM2.5 6.0, PM10 6.0 μg/m3
    2020-09-27 17:17:30: PM1 0.0, PM2.5 6.0, PM10 6.0 μg/m3
    2020-09-27 17:17:40: PM1 0.0, PM2.5 5.0, PM10 5.0 μg/m3    
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMSx003 -n 10 -i 10 serial -f csv
    ```

    ``` csv
    time, raw01, raw25, raw10, pm01, pm25, pm10, n0_3, n0_5, n1_0, n2_5, n5_0, n10_0
    1601219780, 0, 7, 7, 0.0, 7.0, 7.0, 2.10, 0.70, 0.45, 0.30, 0.00, 0.00
    1601219790, 0, 7, 7, 0.0, 7.0, 7.0, 1.89, 0.63, 0.42, 0.27, 0.00, 0.00
    1601219800, 0, 7, 7, 0.0, 7.0, 7.0, 1.80, 0.60, 0.39, 0.24, 0.00, 0.00
    1601219810, 0, 7, 7, 0.0, 7.0, 7.0, 1.80, 0.60, 0.39, 0.24, 0.00, 0.00
    1601219820, 0, 6, 6, 0.0, 6.0, 6.0, 1.80, 0.60, 0.29, 0.21, 0.00, 0.00
    1601219830, 0, 6, 6, 0.0, 6.0, 6.0, 1.80, 0.60, 0.29, 0.21, 0.00, 0.00
    1601219840, 0, 6, 6, 0.0, 6.0, 6.0, 1.59, 0.53, 0.26, 0.18, 0.00, 0.00
    1601219850, 0, 6, 6, 0.0, 6.0, 6.0, 1.59, 0.53, 0.26, 0.18, 0.00, 0.00
    1601219860, 0, 5, 5, 0.0, 5.0, 5.0, 1.38, 0.46, 0.23, 0.15, 0.00, 0.00
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMSx003 -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    00000000: 42 4d 00 1c 00 00 00 08 00 08 00 00 00 08 00 08 00 d2 00 46 00 2d 00 1e 00 00 00 00 97 00 02 c5  BM.................F.-..........
    00000020: 42 4d 00 1c 00 00 00 07 00 07 00 00 00 07 00 07 00 d2 00 46 00 2d 00 1e 00 00 00 00 97 00 02 c1  BM.................F.-..........
    00000040: 42 4d 00 1c 00 00 00 07 00 07 00 00 00 07 00 07 00 bd 00 3f 00 2a 00 1b 00 00 00 00 97 00 02 9f  BM.................?.*..........
    00000060: 42 4d 00 1c 00 00 00 07 00 07 00 00 00 07 00 07 00 b4 00 3c 00 27 00 18 00 00 00 00 97 00 02 8d  BM.................<.'..........
    00000080: 42 4d 00 1c 00 00 00 07 00 07 00 00 00 07 00 07 00 b4 00 3c 00 27 00 18 00 00 00 00 97 00 02 8d  BM.................<.'..........
    000000a0: 42 4d 00 1c 00 00 00 06 00 06 00 00 00 06 00 06 00 b4 00 3c 00 1d 00 15 00 00 00 00 97 00 02 7c  BM.................<...........|
    000000c0: 42 4d 00 1c 00 00 00 06 00 06 00 00 00 06 00 06 00 b4 00 3c 00 1d 00 15 00 00 00 00 97 00 02 7c  BM.................<...........|
    000000e0: 42 4d 00 1c 00 00 00 06 00 06 00 00 00 06 00 06 00 9f 00 35 00 1a 00 12 00 00 00 00 97 00 02 5a  BM.................5...........Z
    00000100: 42 4d 00 1c 00 00 00 06 00 06 00 00 00 06 00 06 00 9f 00 35 00 1a 00 12 00 00 00 00 97 00 02 5a  BM.................5...........Z
    00000120: 42 4d 00 1c 00 00 00 05 00 05 00 00 00 05 00 05 00 8a 00 2e 00 17 00 0f 00 00 00 00 97 00 02 34  BM.............................4
    ```

## PMS5003T

=== "info"

    About the PMS5003T sensor (`-m PMS5003T`)

    ``` bash
    pms -m PMS5003T info
    ```

    ``` man
    Plantower PMS5003T sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]
    n0_3, n0_5, n1_0, n2_5                  number concentrations over X.Y um [#/cm3]
    temp                                    temperature [°C]
    rhum                                    relative humidity [%]

    String formats: pm (default), raw, cf, num, atm, csv and header
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMS5003S -n 10 -i 10 serial
    ```

    ``` csv
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMS5003T -n 10 -i 10 serial -f csv
    ```

    ``` csv
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMS5003T -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    00000000: 42 4d 00 1c 00 17 00 27 00 29 00 16 00 23 00 29 10 08 04 a9 01 16 00 0c 00 d4 00 e0 9a 00 04 aa  BM.....'.)...#.)................
    00000020: 42 4d 00 1c 00 15 00 24 00 24 00 14 00 21 00 24 0d c8 04 1f 00 e4 00 0e 00 d4 00 e0 9a 00 05 99  BM.....$.$...!.$................
    00000040: 42 4d 00 1c 00 15 00 25 00 26 00 14 00 22 00 26 0f 00 04 66 00 fa 00 16 00 d4 00 e0 9a 00 05 3e  BM.....%.&...".&...f...........>
    00000060: 42 4d 00 1c 00 14 00 23 00 2a 00 13 00 20 00 2a 0e a6 04 37 01 06 00 1e 00 d4 00 df 9a 00 04 ca  BM.....#.*... .*...7............
    00000080: 42 4d 00 1c 00 17 00 26 00 26 00 16 00 23 00 26 0e e8 04 62 01 1e 00 0e 00 d4 00 e0 9a 00 05 44  BM.....&.&...#.&...b...........D
    000000a0: 42 4d 00 1c 00 16 00 25 00 27 00 15 00 22 00 27 0e fd 04 5a 01 20 00 14 00 d4 00 df 9a 00 05 56  BM.....%.'...".'...Z. .........V
    000000c0: 42 4d 00 1c 00 16 00 24 00 2a 00 15 00 21 00 2a 0e af 04 56 01 1a 00 16 00 d4 00 df 9a 00 05 04  BM.....$.*...!.*...V............
    000000e0: 42 4d 00 1c 00 17 00 25 00 2d 00 16 00 22 00 2d 0e fd 04 6f 01 24 00 16 00 d5 00 de 9a 00 05 7f  BM.....%.-...".-...o.$..........
    00000100: 42 4d 00 1c 00 15 00 23 00 2c 00 14 00 20 00 2c 0e ca 04 5a 01 1e 00 18 00 d5 00 de 9a 00 05 29  BM.....#.,... .,...Z...........)
    00000120: 42 4d 00 1c 00 14 00 22 00 2b 00 13 00 20 00 2b 0e 13 04 14 01 10 00 1e 00 d5 00 df 9a 00 04 20  BM.....".+... .+............... 
    ```

## PMS5003S

=== "info"

    About the PMS5003S sensor (`-m PMS5003S`)

    ``` bash
    pms -m PMS5003S info
    ```

    ``` man
    Plantower PMS5003S sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations over X.Y um [#/cm3]
    HCHO                                    formaldehyde concentration [mg/m3]

    String formats: pm (default), raw, cf, num, hcho, csv and header
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMS5003S -n 10 -i 10 serial
    ```

    ``` csv
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMS5003S -n 10 -i 10 serial -f csv
    ```

    ``` hexdump
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMS5003S -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    ```

## PMS5003ST

=== "info"

    About the PMS5003ST sensor (`-m PMS5003ST`)

    ``` bash
    pms -m PMS5003ST info
    ```

    ``` man
    Plantower PMS5003ST sensor observations

    time                                    measurement time [seconds since epoch]
    raw01, raw25, raw10                     cf=1 PM estimates [μg/m3]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]
    n0_3, n0_5, n1_0, n2_5, n5_0, n10_0     number concentrations over X.Y um [#/cm3]
    HCHO                                    formaldehyde concentration [mg/m3]
    temp                                    temperature [°C]
    rhum                                    relative humidity [%]

    String formats: pm (default), raw, cf, num, hcho, atm, csv and header
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m PMS5003ST -n 10 -i 10 serial
    ```

    ``` csv
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m PMS5003ST -n 10 -i 10 serial -f csv
    ```

    ``` csv
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m PMS5003ST -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    ```
