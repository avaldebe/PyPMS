# [Senserion][] sensors

| Sensor | `--sensor-model` |  PM1  | PM2.5 |  PM4  | PM10  | size bins | Other                 | Datasheet   | Dimensions | Connector |
| ------ | ---------------- | :---: | :---: | :---: | :---: | :-------: | --------------------- | ----------- | ---------- | --------- |
| SPS30  | [`SPS30`][]      |   X   |   X   |   X   |   X   |     5     | typical particle size | [en][SPS30] |            | [5 pin][] |

[Senserion]: https://www.sensirion.com/en/environmental-sensors/particulate-matter-sensors-pm25/
[SPS30]: https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/9.6_Particulate_Matter/Datasheets/Sensirion_PM_Sensors_SPS30_Datasheet.pdf

[`SPS30`]:  #SPS30
[5 pin]:    #5_Pin_connector

## 5 Pin connector

5 pin JST ZH (1.50mm pitch)

| Pin | Name   | Voltage      | Function                       |
| --- | ------ | ------------ | ------------------------------ |
| 1   | VDD    | 5V±10%       |
| 2   | RX/SDA | 3.3V/5V TTL  | serial port/I2C                |
| 3   | TX/SCL | 3.3V/5V TTL  | serial port/I2C                |
| 4   | SEL    | floating/GND | floating for UART, GND for I2C |
| 5   | GND    | 0V           |

## Serial communication

Serial protocol is UART 115200 8N1 [5V TTL, LVTTL 3.3V compatible].

### Commands

The [`SPS30`][] only support continuous operation, at about one measurement per second.
However, new measurements are not streamed. Each measurement has to requested.
This behavior is consistent with `passive_mode`/single-shot operation in other sensors.
The `sleep`/`wake` commands listed here (stop measurement/start measurement on the [datasheet][SPS30]),
behave consistently with the rest of the supported PM sensors.
There are also `deep-sleep`/`wake-up` commands (sleep/wake-up on the [datasheet][SPS30]),
which are not implemented. As `deep-sleep` disable the UART interface and `wake-up` is a 2 stage procedure.

| Command        | Description              | `message`                 |
| -------------- | ------------------------ | ------------------------- |
| `active_mode`  | continuous operation     | N/A                       |
| `passive_mode` | single-shot operation    | N/A                       |
| `passive_read` | request last measurement | `7E 00 03 00 FC 7E`       |
| `sleep`        | idle mode                | `7E 00 01 00 FE 7E`       |
| `wake`         | wake up from idle mode   | `7E 00 00 02 01 03 F9 7E` |

### Measurements

Messages containing measurements consist of floats.
The second to last bit of the message should contain `0xFF-sum(message[1:-2])%0x100`.

| `message` | [`SPS30`][]      |
| --------- | ---------------- |
|           | 47 bits          |
| header    | 5 bits           |
|           | `7E 00 03 00 28` |
| body      | 40 bits          |
|           | 10 values        |
| checksum  | 1 bit            |
| tail      | 1 bit            |
|           | `7E`             |

### SPS30

The message body (`message[5:-2]`) contains 10 values:

- pm01, pm25, pm04, pm10: PM1.0, PM2.5, PM4.0, PM10 [ug/m³]
- n0_5, n1_0, n2_5, n4_0, n10_0: number concentrations under X.Y um [#/cm³]
- diam: typical particle size [μm]

The following hexdump (`xxd -g1 -c47`) shows one message per line

```hexdump
```
