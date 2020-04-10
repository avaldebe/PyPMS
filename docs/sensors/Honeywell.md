# [Honeywell][] sensors

| Sensor    | `--sensor-model` |  PM1  | PM2.5 |  PM4  | PM10  | Datasheet     | Dimensions   | Connector  |
| --------- | ---------------- | :---: | :---: | :---: | :---: | ------------- | ------------ | ---------- |
| HPMA115S0 | [`HPMA115S0`][]  |       |   X   |       |   X   | [en][HPMA115] | 43x36x24 mm³ | [8 pin][]  |
| HPMA115C0 | [`HPMA115C0`][]  |   X   |   X   |   X   |   X   | [en][HPMA115] | 44X36X12 mm³ | [10 pin][] |

[Honeywell]: https://sensing.honeywell.com/sensors/particle-sensors/hpm-series
[HPMA115]: https://sensing.honeywell.com/honeywell-sensing-particulate-hpm-series-datasheet-32322550


[`HPMA115S0`]:#HPMA115S0
[`HPMA115C0`]:#HPMA115C0
[8 pin]:      #8_Pin_connector
[10 pin]:     #10_Pin_connector

## WARNING

This sensors are 3.3V devices. They require 5V power to operate the laser and fan.
However, the I/O pins are not 5V tolerant and the sensor will be damaged by 5V logic.

## 8 Pin connector

8 pin Molex 1.25mm "PicoBlade" 51021 compatible, found online as 1.25mm JST.

| Pin | Name | Voltage  | Function                                |
| --- | ---- | -------- | --------------------------------------- |
| 1   | VOUT | 3.3V     | power output: max 100 mA                |
| 2   | VCC  | 5V±0.2V  | power input: max 600 mA, ripple < 20 mV |
| 3/4 | NC   |          | not connected                           |
| 5   | RES  |          | reserved for future use                 |
| 6   | TX   | 3.3V TTL | serial port                             |
| 7   | RX   | 3.3V TTL | serial port                             |
| 8   | GND  | 0V       |

## 10 Pin connector

5x2 1.27mm female header: Samtec SFSD-05-28-H-5.00-SR (cable assembly) or SFM-105-02-H-D (surface mount).

| Pin | Name | Voltage  | Function                                |
| --- | ---- | -------- | --------------------------------------- |
| 1   | VOUT | 5V       | power output: max 300 mA                |
| 2   | VCC  | 5V±0.2V  | power input: max 600 mA, ripple < 20 mV |
| 3/4 | GND  | 0V       |
| 5   | RES  |          | reserved for future use                 |
| 6   | NC   |          | not connected                           |
| 7   | RX   | 3.3V TTL | serial port                             |
| 8   | NC   |          | not connected                           |
| 9   | TX   | 3.3V TTL | serial port                             |
| 10  | SET  |          | reserved for future use                 |

## Serial communication

Serial protocol is UART 9600 8N1 ([3.3V TTL](#warning)).

### Commands

All the Honeywell PM sensors can be fully controlled with serial commands:

| Command        | Description                     | `message`     |
| -------------- | ------------------------------- | ------------- |
| `active_mode`  | continuous operation            | `68 01 40 57` |
| `passive_mode` | single-shot operation           | `68 01 20 77` |
| `passive_read` | trigger single-shot measurement | `68 01 04 93` |
| `sleep`        | sleep mode                      | `68 01 02 95` |
| `wake`         | wake up from sleep mode         | `68 01 01 96` |

### Measurements

Messages containing measurements consist of unsigned short integers.
The last bit of the message should contain `sum(message[3:-1])%0x100`.

| `message` | [`HPMA115S0`][]             | [`HPMA115C0`][]              |
| --------- | --------------------------- | ---------------------------- |
|           | 8 bits (32b on active mode) | 16 bits (32b on active mode) |
| header    | 3 bits                      | 3 bits                       |
|           | `40 05 04`                  | `40 05 04`                   |
| body      | 4 bits                      | 12 bits                      |
|           | 2 values                    | 4 values, 2 reserved         |
| checksum  | 1 bit                       | 1 bit                        |

### HPMA115S0

The message body (`message[3:7]`) contains 2 values:

- pm25, pm10: PM2.5, PM10 [μg/m³]

The following hexdump (`xxd -g1 -c8`) shows one message per line

```hexdump
```

### HPMA115C0

The message body (`message[3:7]`) contains 4 values:

- pm01, pm25, pm04, pm10: PM1.0, PM2.5, PM4.0 PM10 [μg/m³]

The following hexdump (`xxd -g1 -c16`) shows one message per line

```hexdump
```
