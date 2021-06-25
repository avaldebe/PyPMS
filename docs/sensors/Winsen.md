# [Winsen] sensors

| Sensor  | `--sensor-model` |  PM1  | PM2.5 | PM10  | CO2 | Datasheet  | Dimensions   | Connector |
| ------- | ---------------- | :---: | :---: | :---: | --- | ---------- | ------------ | --------- |
| ZH03B   | not supported    |   X   |   X   |   X   |     | [en][zh03] | 50x32x21 mm³ | 8 pin     |
| ZH06-I  | not supported    |   X   |   X   |   X   |     | [en][zh06] | 47×37×12 mm³ | 8 pin     |
| MH-Z19B | [`MHZ19B`][]     |       |       |       | X   | [en][z19b] | 40×20×9 mm³  | 7 pin     |

[Winsen]:https://www.winsen-sensor.com
[zh03]:  https://www.winsen-sensor.com/d/files/ZH03B.pdf
[zh06]:  https://www.winsen-sensor.com/d/files/ZH06.pdf
[z19b]:  https://www.winsen-sensor.com/d/files/infrared-gas-sensor/ndir-co2-sensor/mh-z19b-co2-manual(ver1_6).pdf

[`MHZ19B`]:  #MHZ19B
[7 pin]:     #7_Pin_connector

## WARNING

This sensors are 3.3V devices. They require 5V power to operate.
However, on some sensors the I/O pins are not 5V tolerant and the sensor will be damaged by 5V logic.

## 7 Pin connector

7 pin Molex 1.25mm "PicoBlade" 51021 compatible, found online as 1.25mm JST.

| Pin | Name | Voltage  | Function    |
| --- | ---- | -------- | ----------- |
| 1/2 |      |          | reserved    |
| 3   | GND  | 0V       |
| 4   | VCC  | 5V       |
| 5   | RX   | 3.3V TTL | serial port |
| 6   | TX   | 3.3V TTL | serial port |
| 7   |      |          | reserved    |

## Serial communication

Serial protocol is UART 9600 8N1 ([3.3V TTL](#warning)).
The [`MHZ19B`][] datasheet advertized interface as 5V tolerant.
However, the this sensor has only been tested with a 3.3V interface.

### Commands

| Command         | Description                           | `message`                    |
| --------------- | ------------------------------------- | ---------------------------- |
| `passive_read`  | read CO2 concentration                | `FF 01 86 00 00 00 00 00 79` |
| not implemented | 400 ppm CO2 (zero point) calibration  | `FF 01 87 00 00 00 00 00 78` |
| not implemented | 1000 ppm CO2 (span point) calibration | `FF 01 88 03 E8 00 00 00 8C` |
| not implemented | 2000 ppm CO2 (span point) calibration | `FF 01 88 07 D0 00 00 00 A0` |

### Measurements

Messages containing measurements consist of unsigned short integers.
The last bit of the message should contain `0x100 - sum(message[1:-1]) % 0x100`.

| `message` | [`MHZ19B`][]         |
| --------- | -------------------- |
|           | 9 bits               |
| header    | 2 bit                |
|           | `FF 86`              |
| body      | 6 bits               |
|           | 1 values, 2 reserved |
| checksum  | 1 bits               |

### MHZ19B

The message body (`message[2:4]`) contains 1 value:

- co2: CO2 concentration [ppm]

The following hexdump (`pms -m MHZ19B -n 10 -i 10 serial -f hexdump`) shows one message per line

```hexdump
```
