"""
Bosh Sensortec sensors on MCU bridge modules
- messages are 7-20b long
"""

import struct
from dataclasses import dataclass, field
from typing import Tuple

from pms import SensorWarmingUp, WrongMessageChecksum, WrongMessageFormat

from .. import base

ALIASES = ("BME680",)

commands = base.Commands(
    passive_read=base.Cmd(b"\xA5\x56\x01\xFC", b"\x5A\x5A\x3F\x0F", 20),
    passive_mode=base.Cmd(b"\xA5\x56\x01\xFC", b"\x5A\x5A\x3F\x0F", 20),
    active_mode=base.Cmd(b"\xA5\x56\x02\xFD", b"\x5A\x5A\x3F\x0F", 20),
    sleep=base.Cmd(b"", b"", 0),
    wake=base.Cmd(b"", b"", 0),
)


class Message(base.Message):
    """Messages from mcu680 modules with a BME680 sensor"""

    data_records = slice(7)

    @property
    def header(self) -> bytes:
        return self.message[:4]

    @property
    def payload(self) -> bytes:
        return self.message[4:-1]

    @property
    def checksum(self) -> int:
        return self.message[-1]

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> base.Message:

        # consistency check: bug in message singnature
        assert len(header) == 4, f"wrong header length {len(header)}"
        assert header[:2] == b"ZZ", f"wrong header start {header!r}"
        len_payload = header[-1]
        assert length == len_payload + 5, f"wrong payload length {length}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header!r}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)}")
        checksum = (sum(msg.header) + sum(msg.payload)) % 0x100
        if msg.checksum != checksum:
            raise WrongMessageChecksum(f"message checksum {msg.checksum} != {checksum}")
        if sum(msg.payload) == 0:
            raise SensorWarmingUp(f"message empty: warming up sensor")
        return msg

    @staticmethod
    def _unpack(message: bytes) -> Tuple[int, ...]:
        return struct.unpack(f">hHHBHLh", message)


@dataclass(frozen=False)
class ObsData(base.ObsData):
    """
    Bosh Sensortec BME680 sensor observations

    time                                    measurement time [seconds since epoch]
    temp                                    temperature [°C]
    rhum                                    relative humidity [%]
    pres                                    atmospheric pressure [hPa]
    IAQ_acc                                 IAQ accuracy flag
    IAQ                                     index of air quality [0--500]
    gas                                     gas resistance [kΩ]
    alt                                     altitude estimate [m above sea level]

    String formats: atm, bme (default), bsec, csv and header
    """

    # temp[°C],rhum[%]: temperature,relative humidity (read as 100*temp,100*rhum)
    temp: float = field(metadata=base.metadata("temperature", "°C", "degrees"))
    rhum: float = field(metadata=base.metadata("relative humidity", "%", "percentage"))
    # press[hPa]: atm. pressure (read as 24b in hPa)
    # on read press XSB(8b)|MSB(8b)
    pres: float = field(metadata=base.metadata("atmospheric pressure", "hPa", "pressure"))
    # on read press LSB(8b)
    IAQ_acc: int = field(metadata=base.metadata("IAQ acc", "1", "acc"))
    # on read IAQ_acc(4b)|IAQ(12b) packed into 16b
    IAQ: int = field(metadata=base.metadata("IAQ", "0-500", "iaq"))
    gas: int = field(metadata=base.metadata("gas resistance", "kΩ", "resistance"))
    alt: int = field(metadata=base.metadata("altitude estimate", "m(a.s.l.)", "elevation"))

    def __post_init__(self):
        """Units conversion
        temp [°C]   read in [0.01 °C]
        rhum [%]    read in [1/10 000]
        pres [hPa]  read in [Pa] across 12b
        gas  [kΩ]   read in [Ω]
        """
        self.temp /= 100
        self.rhum /= 100
        self.pres = (int(self.pres) << 8 | self.IAQ_acc) / 100
        self.IAQ_acc = self.IAQ >> 4
        self.IAQ &= 0x0FFF
        self.gas /= 1000

    def __format__(self, spec: str) -> str:
        if spec == "atm":
            return f"{self.date:%F %T}: Temp. {self.temp:.1f} °C, Rel.Hum. {self.rhum:.1f} %, Press {self.pres:.2f} hPa"
        if spec == "bme":
            return f"{self.date:%F %T}: Temp. {self.temp:.1f} °C, Rel.Hum. {self.rhum:.1f} %, Press {self.pres:.2f} hPa, {self.gas:.1f} kΩ"
        if spec == "bsec":
            return f"{self.date:%F %T}: Temp. {self.temp:.1f} °C, Rel.Hum. {self.rhum:.1f} %, Press {self.pres:.2f} hPa, {self.IAQ} IAQ"
        if spec == "csv":
            return f"{self.time}, {self.temp:.1f}, {self.rhum:.1f}, {self.pres:.2f}, {self.IAQ_acc}, {self.IAQ}, {self.gas:.1f}, {self.alt}"

        return super().__format__(spec)

    def __str__(self):
        return self.__format__("bme")
