# [Plantower][] sensors

| Sensor    | `--sensor-model` |  PM1  | PM2.5 | PM10  | size bins | Other                  | Datasheet                     | Dimensions   | Connector  |
| --------- | ---------------- | :---: | :---: | :---: | :-------: | ---------------------- | ----------------------------- | ------------ | ---------- |
| PMS1003   | [`PMSx003`][]    |   X   |   X   |   X   |     6     |                        | [en][g1_aqmd],  [cn][g1_lcsc] | 42x65x23 mm³ | [8 pin][]  |
| PMS3003   | [`PMS3003`][]    |   X   |   X   |   X   |           | No passive mode read   | [en][g3_aqmon], [cn][g3_lcsc] | 43x50x21 mm³ | [8 pin][]  |
| PMS5003   | [`PMSx003`][]    |   X   |   X   |   X   |     6     |                        | [en][g5_aqmd],  [cn][g5_lcsc] | 38x50x21 mm³ | [8 pin][]  |
| PMS5003T  | [`PMS5003T`][]   |   X   |   X   |   X   |     4     | temp. & rel.hum.       |                               | 38x50x21 mm³ | [8 pin][]  |
| PMS5003S  | [`PMS5003S`][]   |   X   |   X   |   X   |     6     | HCHO concentration     |                               | 38x50x21 mm³ | [8 pin][]  |
| PMS5003ST | [`PMS5003ST`][]  |   X   |   X   |   X   |     6     | HCHO, temp. & rel.hum. |                               | 38x50x21 mm³ | [8 pin][]  |
| PMS7003   | [`PMSx003`][]    |   X   |   X   |   X   |     6     |                        | [cn][g7_lcsc]                 | 37x48x12 mm³ | [10 pin][] |
| PMSA003   | [`PMSx003`][]    |   X   |   X   |   X   |     6     |                        | [cn][gA_lcsc]                 |              | [10 pin][] |

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

[`PMSx003`]:  #PMSx003
[`PMS3003`]:  #PMS3003
[`PMS5003T`]: #PMS5003T
[`PMS5003S`]: #PMS5003S
[`PMS5003ST`]:#PMS5003ST
[8 pin]:      #8_Pin_connector
[10 pin]:     #10_Pin_connector

## WARNING

This sensors are 3.3V devices. They require 5V power to operate the laser and fan.
However, the I/O pins are not 5V tolerant and the sensor will be damaged by 5V logic.

## 8 Pin connector

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

## 10 Pin connector

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

## Serial communication

Serial protocol is UART 9600 8N1 ([3.3V TTL](#warning)).

### Commands

With the exception of the [`PMS3003`][], all the Plantower PM sensors
can be fully controlled with serial commands:

| Command        | Description                     | `message`              |
| -------------- | ------------------------------- | ---------------------- |
| `active_mode`  | continuous operation            | `42 4D E1 00 01 01 71` |
| `passive_mode` | single-shot operation           | `42 4D E1 00 00 01 70` |
| `passive_read` | trigger single-shot measurement | `42 4D E2 00 00 01 71` |
| `sleep`        | sleep mode                      | `42 4D E4 00 00 01 73` |
| `wake`         | wake up from sleep mode         | `42 4D E4 00 01 01 74` |

### Measurements

Messages containing measurements consist of unsigned short integers.
The last 2 bits of the message should contain `sum(message[:2])`.

| `message` | [`PMS3003`][]        | [`PMSx003`][]         | [`PMS5003T`][] | [`PMS5003S`][] | [`PMS5003ST`][]       |
| --------- | -------------------- | --------------------- | -------------- | -------------- | --------------------- |
|           | 24 bits              | 32 bits               | 32 bits        | 32 bits        | 40 bits               |
| header    | 4 bits               | 4 bits                | 4 bits         | 4 bits         | 4 bits                |
|           | `42 4d 00 14`        | `42 4d 00 1c`         | `42 4d 00 1c`  | `42 4d 00 1c`  | `42 4d 00 24`         |
| body      | 18 bits              | 26 bits               | 26 bits        | 26 bits        | 34 bits               |
|           | 6 values, 3 reserved | 12 values, 1 reserved | 13 values      | 13 values      | 15 values, 2 reserved |
| checksum  | 2 bits               | 2 bits                | 2 bits         | 2 bits         | 2 bits                |

### PMS3003

The message body (`message[4:16]`) contains 6 values:

- raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
- pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]

The following hexdump (`pms -m PMS3003 -n 10 -i 10 serial -f hexdump`) shows one message per line

```hexdump
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

### PMSx003

The message body (`message[4:28]`) contains 12 values:

- raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
- pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]
- n0_3, n0_5, n1_0, n2_5, n5_0, n10_0: number of particles under X_Y μm [#/cm³] (raw values [#/100 cm³])

The following hexdump (`pms -m PMSx003 -n 10 -i 10 serial -f hexdump`) shows one message per line

```hexdump
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

### PMS5003T

The message body (`message[4:28]`) contains 12 values:

- raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
- pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]
- n0_3, n0_5, n1_0, n2_5: number of particles under X_Y um [#/cm³] (raw values [#/100 cm³])
- temp: temperature [°C]
- rhum: relative humidity [%]

The following hexdump (`pms -m PMS5003T -n 10 -i 10 serial -f hexdump`) shows one message per line

```hexdump
```

### PMS5003S

The message body (`message[4:30]`) contains 13 values:

- raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
- pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]
- n0_3, n0_5, n1_0, n2_5, n5_0, n10_0: number of particles under X_Y um [#/cm³] (raw values [#/100 cm³])
- HCHO: concentration of formaldehyde [μg/m³]

The following hexdump (`pms -m PMS5003S -n 10 -i 10 serial -f hexdump`) shows one message per line

```hexdump
```

### PMS5003ST

The message body (`message[4:34]`) contains 15 values:

- raw01, raw25, raw10: cf=1 PM estimates [μg/m³]
- pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]
- n0_3, n0_5, n1_0, n2_5, n5_0, n10_0: number of particles under X_Y um [#/cm³] (raw values [#/100 cm³])
- HCHO: concentration of formaldehyde [μg/m³]
- temp: temperature [°C]
- rhum: relative humidity [%]

The following hexdump (`pms -m PMS5003ST -n 10 -i 10 serial -f hexdump`) shows one message per line

```hexdump
```
