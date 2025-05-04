# [NovaFitness] sensors

!!! warning
    This sensors are 3.3V devices. They require 5V power to operate the laser and fan.
    However, the I/O pins are not 5V tolerant and the sensor will be damaged by 5V logic.

=== "sensor"

    | Sensor | `--sensor-model` |      PM2.5       |       PM10       |      PM100       |
    | ------ | ---------------- | :--------------: | :--------------: | :--------------: |
    | SDS011 | [SDS01x]         | :material-check: | :material-check: |                  |
    | SDS018 | [SDS01x]         | :material-check: | :material-check: |                  |
    | SDS021 | [SDS01x]         | :material-check: | :material-check: |                  |
    | SDS198 | [SDS198]         |                  |                  | :material-check: |

=== "datasheet"

    | Sensor | Datasheet    | Dimensions   | Connector |
    | ------ | ------------ | ------------ | --------- |
    | SDS011 | [en][SDS011] | 70x70x25 mm³ | [7 Pin]   |
    | SDS018 | [en][SDS018] | 60x46x20 mm³ | [7 Pin]   |
    | SDS021 | [en][SDS021] | 43x32x24 mm³ | [5 Pin]   |
    | SDS198 | [en][SDS198] | 70x70x25 mm³ | [7 Pin]   |

[NovaFitness]: http://inovafitness.com/en/a/index.html
[SDS011]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS011%20laser%20PM2.5%20sensor%20specification-V1.3.pdf
[SDS018]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS018%20Laser%20PM2.5%20Product%20Spec%20V1.5.pdf
[SDS021]: https://cdn.sparkfun.com/assets/parts/1/2/2/7/5/SDS021_laser_PM2.5_sensor_specification-V1.0.pdf
[SDS198]: https://www-sd-nf.oss-cn-beijing.aliyuncs.com/官网下载/SDS198%20laser%20PM100%20sensor%20specification-V1.2.pdf

[SDS01x]: #sds01x
[SDS198]: #sds198
[5 pin]:  #connector
[7 pin]:  #connector

## Connector

=== "5 pin"

    5 pin ????, comes with sensor

    | Pin | Name | Voltage  | Function            |
    | --- | ---- | -------- | ------------------- |
    | 1   | 5V   | 4.7-5.3V | >1W, ripple < 20 mV |
    | 2   | NC   |          | not connected       |
    | 3   | GND  | 0V       |
    | 4   | R    | 3.3V TTL | RX serial port      |
    | 5   | T    | 3.3V TTL | TX serial port      |

=== "7 pin"

    7 pin JST XH (2.5mm pitch), comes with sensor

    | Pin | Name  | Voltage  | Function                              |
    | --- | ----- | -------- | ------------------------------------- |
    | 1   | NC    |          | not connected                         |
    | 2   | 1μm   | 3.3V PWM | PM2.5 0-999 μg/m³; reserved on SDS198 |
    | 3   | 5V    | 4.7-5.3V | >1W, ripple < 20 mV                   |
    | 4   | 2.5μm | 3.3V PWM | PM10 0-999 μg/m³; reserved on SDS198  |
    | 5   | GND   | 0V       |
    | 6   | R     | 3.3V TTL | RX serial port                        |
    | 7   | T     | 3.3V TTL | TX serial port                        |

## Protocol

Serial protocol is UART 9600 8N1 :material-alert: 3.3V TTL.

=== "commands"

    All the NovaFitness PM sensors
    can be fully controlled with serial commands:

    | Command        | Description                     | `message`                                                  |
    | -------------- | ------------------------------- | ---------------------------------------------------------- |
    | `active_mode`  | continuous operation            | `aa b4 02 01 00 00 00 00 00 00 00 00 00 00 00 ff ff 01 ab` |
    | `passive_mode` | single-shot operation           | `aa b4 02 01 01 00 00 00 00 00 00 00 00 00 00 ff ff 02 ab` |
    | `passive_read` | trigger single-shot measurement | `aa b4 04 00 00 00 00 00 00 00 00 00 00 00 00 ff ff 02 ab` |
    | `sleep`        | sleep mode                      | `aa b4 06 01 00 00 00 00 00 00 00 00 00 00 00 ff ff 05 ab` |
    | `wake`         | wake up from sleep mode         | `aa b4 06 01 01 00 00 00 00 00 00 00 00 00 00 ff ff 06 ab` |

=== "message"

    Messages containing measurements consist of unsigned short integers.
    The second to last bit of the message should contain `sum(message[2:-2])%0x100`.

    | `message` | [SDS01x]       | [SDS198]                  |
    | --------- | -------------- | ------------------------- |
    |           | 10 bits        | 10 bits                   |
    | header    | 2 bits         | 2 bits                    |
    |           | `aa c0`        | `aa cf`                   |
    | body      | 6 bits         | 6 bits                    |
    |           | 2 values, 1 ID | 1 reserved, 1 value, 1 ID |
    | checksum  | 1 bit          | 1 bit                     |
    | tail      | 1 bit          | 1 bit                     |
    |           | `ab`           | `ab`                      |

=== "SDS01x"

    The message body (`message[2:6]`) contains 2 values:

    - pm25, pm10: PM2.5, PM10 [μg/m³] (raw values [0.1 μg/m³])

=== "SDS198"

    The message body (`message[4:6]`) contains 1 value:

    - pm100: PM100 [μg/m³]

## SDS01x

=== "info"

    About the sensors supported by the SDS01x protocol (`-m SDS01x`)

    ``` bash
    pms -m SDS01x info
    ```

    ``` man
    --8<-- "SDS01x.info"
    ```

=== "serial"

    Read 10 samples (`-n 10`), one sample every 10 seconds (`-i 10`)

    ``` bash
    pms -m SDS01x -n 10 -i 10 serial
    ```

    ``` csv
    --8<-- "SDS01x.txt"
    ```

=== "csv"

    Print on CSV format (`-f csv`)

    ``` bash
    pms -m SDS01x -n 10 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "SDS01x.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)

    ```bash
    pms -m SDS01x -n 10 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "SDS01x.hexdump"
    ```

## SDS198

=== "info"

    About the SDS198 sensor (`-m SDS198`)

    ``` bash
    pms -m SDS198 info
    ```

    ``` man
    --8<-- "SDS198.info"
    ```

=== "serial"

    Read 6 samples (`-n 6`), one sample every 10 seconds `(-i 10`)

    ``` bash
    pms -m SDS198 -n 6 -i 10 serial
    ```

    ``` csv
    --8<-- "SDS198.txt"
    ```

=== "csv"

    Print on CSV format (-f csv)

    ``` bash
    pms -m SDS198 -n 6 -i 10 serial -f csv
    ```

    ``` csv
    --8<-- "SDS198.csv"
    ```

=== "hexdump"

    Print on hexdump format (`-f hexdump`)


    ``` bash
    pms -m SDS198 -n 6 -i 10 serial -f hexdump
    ```

    ``` hexdump
    --8<-- "SDS198.hexdump"
    ```
