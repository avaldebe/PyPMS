# [Winsen] sensors

!!! warning
    This sensors are 3.3V devices. They require 5V power to operate.
    However, on some sensors the I/O pins are not 5V tolerant and the sensor will be damaged by 5V logic.

=== "sensor"

    | Sensor  | `--sensor-model` |       PM1        |      PM2.5       |       PM10       | CO2              |
    | ------- | ---------------- | :--------------: | :--------------: | :--------------: | ---------------- |
    | MH-Z19B | [MHZ19B]         |                  |                  |                  | :material-check: |
    | ZH03B   | [ZH0xx]          | :material-check: | :material-check: | :material-check: |                  |
    | ZH06-I  | [ZH0xx]          | :material-check: | :material-check: | :material-check: |                  |

=== "datasheet"

    | Sensor  | Datasheet  | Dimensions   | Connector |
    | ------- | ---------- | ------------ | --------- |
    | MH-Z19B | [en][z19b] | 40×20×9 mm³  | [7 pin]   |
    | ZH03B   | [en][zh03] | 50x32x21 mm³ | [8 pin]   |
    | ZH06-I  | [en][zh06] | 47×37×12 mm³ | [8 pin]   |

[Winsen]:https://www.winsen-sensor.com
[zh03]:  https://www.winsen-sensor.com/d/files/ZH03B.pdf
[zh06]:  https://www.winsen-sensor.com/d/files/ZH06.pdf
[z19b]:  https://www.winsen-sensor.com/d/files/infrared-gas-sensor/ndir-co2-sensor/mh-z19b-co2-manual(ver1_6).pdf

[ZH0xx]:   #zh0xx
[MHZ19B]:  #mhz19b
[7 pin]:   #connector
[8 pin]:   #connector

## Connector

=== "7 pin"

    7 pin Molex 1.25mm "PicoBlade" 51021 compatible, found online as 1.25mm JST.

    | Pin | Name | Voltage  | Function    |
    | --- | ---- | -------- | ----------- |
    | 1/2 |      |          | reserved    |
    | 3   | GND  | 0V       |
    | 4   | VCC  | 5V       |
    | 5   | RX   | 3.3V TTL | serial port |
    | 6   | TX   | 3.3V TTL | serial port |
    | 7   |      |          | reserved    |

=== "8 pin"

    8 pin Molex 1.25mm "PicoBlade" 51021 compatible, found online as 1.25mm JST.

    | Pin | Name | Voltage  | Function           |
    | --- | ---- | -------- | ------------------ |
    | 1   | VCC  | 5V       |
    | 2   | GND  | 0V       |
    | 3   |      |          | reserved           |
    | 4   | RX   | 3.3V TTL | serial port        |
    | 5   | TX   | 3.3V TTL | serial port        |
    | 6/7 | NC   |          | reserved           |
    | 8   | PWM  | 3.3V PWM | PM2.5 0-1000 μg/m³ |

## Protocol

Serial protocol is UART 9600 8N1 :material-alert: 3.3V TTL.
!!! note
    The [MHZ19B datasheet][z19b] advertized interface as 5V tolerant.
    However, the this sensor has only been tested with a 3.3V interface.

    The datasheet also mentions that this sensor needs to warm up for 180 s.
    Therefore, no measurements will be requested until the warm up period is completed.

=== "commands"

    | Command        | `--sensor-model`   | Description                           | `message`                    |
    | -------------- | ------------------ | ------------------------------------- | ---------------------------- |
    | `active_mode`  | [ZH0xx]            | continuous operation                  | `FF 01 78 40 00 00 00 00 47` |
    | `passive_mode` | [ZH0xx] & [MHZ19B] | single-shot operation                 | `FF 01 78 41 00 00 00 00 46` |
    | `passive_read` | [ZH0xx]            | trigger single-shot measurement       | `FF 01 86 00 00 00 00 00 79` |
    | `sleep`        | [ZH0xx]            | sleep mode                            | `FF 01 A7 01 00 00 00 00 57` |
    | `wake`         | [ZH0xx]            | wake up from sleep mode               | `FF 01 A7 00 00 00 00 00 58` |
    |                | [MHZ19B]           | 400 ppm CO2 (zero point) calibration  | `FF 01 87 00 00 00 00 00 78` |
    |                | [MHZ19B]           | 1000 ppm CO2 (span point) calibration | `FF 01 88 03 E8 00 00 00 8C` |
    |                | [MHZ19B]           | 2000 ppm CO2 (span point) calibration | `FF 01 88 07 D0 00 00 00 A0` |

=== "message"

    Messages containing measurements consist of unsigned short integers.
    The last bit of the message should contain `0x100 - sum(message[1:-1]) % 0x100`.

    | `message` | [MHZ19B]             | [ZH0xx]  |
    | --------- | -------------------- | -------- |
    |           | 9 bits               | 9        |
    | header    | 2 bits               | 2 bits   |
    |           | `FF 86`              | `FF 86`  |
    | body      | 6 bits               | 6 bits   |
    |           | 1 values, 2 reserved | 3 values |
    | checksum  | 1 bit                | 1 bit    |

=== "MHZ19B"

    The message body (`message[2:4]`) contains 1 value:

    - co2: CO2 concentration [ppm]

=== "ZH0xx"

    The message body (`message[2:8]`) contains 3 values:

    - pm01, pm25, pm10: PM1.0, PM2.5, PM10 [μg/m³]

## MHZ19B

=== "info"

    About the MHZ19B sensor (`-m MHZ19B`)

    ``` bash
    pms -m MHZ19B info
    ```

    ``` man
    Winsen MH-Z19B sensor observations

    time                                    measurement time [seconds since epoch]
    CO2                                     CO2 concentration [ppm]

    String formats: co2 (default), csv and header
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m MHZ19B -n 10 -i 10 serial
    ```

    ``` csv
    --8<-- "MHZ19B.txt"
    ```

=== "csv"

    Print on CSV format (`-f csv`)


    ``` bash
    pms -m MHZ19B -n 10 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "MHZ19B.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ``` bash
    pms -m MHZ19B -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "MHZ19B.hexdump"
    ```

## ZH0xx

=== "info"

    About the sensors supported by the ZH0xx protocol (`-m ZH0xx`)

    ``` bash
    pms -m ZH0xx info
    ```

    ``` csv
    Winsen ZH03B and ZH06-I sensor observations

    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm10                        PM1.0, PM2.5, PM10 [μg/m3]

    String formats: pm (default), csv and header
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m ZH0xx -n 10 -i 10 serial
    ```

    ``` csv
    --8<-- "ZH0xx.txt"
    ```

=== "csv"

    Print on CSV format (`-f csv`)


    ``` bash
    pms -m ZH0xx -n 10 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "ZH0xx.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)


    ``` bash
    pms -m ZH0xx -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "ZH0xx.hexdump"
    ```
