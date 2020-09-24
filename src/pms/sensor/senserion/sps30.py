"""
Senserion SPS30 sensors
- message protocol implements byte-stuffing
- there is no active mode read
- passive read messages are 47b long
- empty read messages are 7b long
"""

from dataclasses import dataclass, field
from typing import Tuple
import struct

from pms import WrongMessageFormat, WrongMessageChecksum, SensorWarmingUp
from pms.sensor import base

commands = base.Commands(
    # Read Measured Values
    passive_read=base.Cmd(b"\x7E\x00\x03\x00\xFC\x7E", b"\x7E\x00\x03\x00\x28", 47),
    passive_mode=base.Cmd(b"", b"", 0),
    active_mode=base.Cmd(b"", b"", 0),
    # Stop Measurement
    sleep=base.Cmd(b"\x7E\x00\x01\x00\xFE\x7E", b"\x7E\x00\x01\x00\x00", 7),
    # Start Measurement
    wake=base.Cmd(b"\x7E\x00\x00\x02\x01\x03\xF9\x7E", b"\x7E\x00\x00", 7),
)


class Message(base.Message):
    """Messages from Senserion SPS30 sensors"""

    data_records = slice(10)

    @property
    def header(self) -> bytes:
        return self.message[:5]

    @property
    def payload(self) -> bytes:
        """byte de-stuffing"""
        p = self.message[5:-2]
        for k, v in {
            b"\x7E": b"\x7D\x5E",
            b"\x7D": b"\x7D\x5D",
            b"\x11": b"\x7D\x31",
            b"\x13": b"\x7D\x33",
        }.items():
            if v in p:  # pragma: no cover
                p = p.replace(v, k)
        return p

    @property
    def checksum(self) -> int:
        return self.message[-2]

    @property
    def tail(self) -> int:
        return self.message[-1]

    @classmethod
    def _validate(cls, message: bytes, header: bytes, length: int) -> base.Message:

        # consistency check: bug in message singnature
        assert len(header) == 5, f"wrong header length {len(header)}"
        assert header[:2] == b"\x7E\x00", f"wrong header start {header!r}"
        assert length in [7, 47], f"wrong payload length {length} != 4||47"
        len_payload = header[-1]
        assert length == len_payload + 7, f"wrong payload length {length} != {len_payload+7}"

        # validate message: recoverable errors (throw away observation)
        msg = cls(message)
        if msg.header != header:
            raise WrongMessageFormat(f"message header: {msg.header!r}")
        if msg.tail != 0x7E:
            raise WrongMessageFormat(f"message tail: {msg.tail:#x}")
        if len(message) != length:
            raise WrongMessageFormat(f"message length: {len(message)} != {length}")
        checksum = 0xFF - (sum(msg.header[1:]) + sum(msg.payload)) % 0x100
        if msg.checksum != checksum:
            raise WrongMessageChecksum(f"message checksum {msg.checksum} != {checksum}")
        if sum(msg.payload) == 0:
            raise SensorWarmingUp(f"message empty: warming up sensor")
        return msg

    @staticmethod
    def _unpack(message: bytes) -> Tuple[float, ...]:
        return struct.unpack(f">{len(message)//4}f", message)


@dataclass(frozen=False)
class ObsData(base.ObsData):
    """SPS30 observations

    time                                    measurement time [seconds since epoch]
    pm01, pm25, pm04, pm10                  PM1.0, PM2.5, PM4.0, PM10 [ug/m3]
    n0_5, n1_0, n2_5, n4_0, n10_0           number concentrations between 0.3 and X.Y um [#/cm3]
    diam                                    typical particle size [μm]
    """

    pm01: float = field(metadata=base.metadata("PM1", "ug/m3", "concentration"))
    pm25: float = field(metadata=base.metadata("PM2.5", "ug/m3", "concentration"))
    pm04: float = field(metadata=base.metadata("PM4", "ug/m3", "concentration"))
    pm10: float = field(metadata=base.metadata("PM10", "ug/m3", "concentration"))
    n0_5: float
    n1_0: float
    n2_5: float
    n4_0: float
    n10_0: float
    diam: float

    def __format__(self, spec: str) -> str:
        if spec == "header":
            return super().__format__(spec)
        if spec == "pm":
            return f"{self.date:%F %T}: PM1 {self.pm01:.1f}, PM2.5 {self.pm25:.1f}, PM4 {self.pm04:.1f}, PM10 {self.pm10:.1f} ug/m3"
        if spec == "csv":
            pm = f"{self.pm01:.1f}, {self.pm25:.1f}, {self.pm04:.1f}, {self.pm10:.1f}"
            num = f"{self.n0_5:.2f}, {self.n1_0:.2f}, {self.n2_5:.2f}, {self.n4_0:.2f}, {self.n10_0:.2f}"
            return f"{self.time}, {pm}, {num}, {self.diam:.1f}"
        if spec == "num":
            return f"{self.date:%F %T}: N0.5 {self.n0_5:.2f}, N1.0 {self.n1_0:.2f}, N2.5 {self.n2_5:.2f}, N4.0 {self.n4_0:.2f}, N10 {self.n10_0:.2f} #/cm3"
        if spec == "diam":
            return f"{self.date:%F %T}: Ø {self.diam:.1f} μm"
        raise ValueError(  # pragma: no cover
            f"Unknown format code '{spec}' "
            f"for object of type '{__name__}.{self.__class__.__name__}'"
        )
