from enum import Enum, auto
from typing import NamedTuple, Optional
from pms import logger
from . import message, obsdata


class Sensor(Enum):
    """Supported PM sensors"""

    PMSx003 = auto()
    PMS3003 = auto()
    SDS01x = auto()

    PMS1003 = PMS5003 = PMS7003 = PMSA003 = PMSx003
    G1, G3, G5, G7, G10 = PMS1003, PMS3003, PMS5003, PMS7003, PMSA003
    SDS011 = SDS018 = SDS01x

    Default = PMSx003

    @property
    def Message(self):
        return getattr(message, self.name)

    @property
    def Data(self):
        return getattr(obsdata, self.name)

    def command(self, command: str) -> bytes:
        """Serial commands (except PMS3003)"""
        return {
            "PMSx003": {
                "passive_mode": b"\x42\x4D\xE1\x00\x00\x01\x70",
                "passive_read": b"\x42\x4D\xE2\x00\x00\x01\x71",
                "active_mode": b"\x42\x4D\xE1\x00\x01\x01\x71",
                "sleep": b"\x42\x4D\xE4\x00\x00\x01\x73",
                "wake": b"\x42\x4D\xE4\x00\x01\x01\x74",
            },
            "PMS3003": {
                "passive_mode": b"",
                "passive_read": b"",
                "active_mode": b"",
                "sleep": b"",
                "wake": b"",
            },
            "SDS01x": {
                "passive_mode": b"\xAA\xB4\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x02\xAB",
                "passive_read": b"\xAA\xB4\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x02\xAB",
                "active_mode": b"\xAA\xB4\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x01\xAB",
                "sleep": b"\xAA\xB4\x06\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x05\xAB",
                "wake": b"\xAA\xB4\x06\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x06\xAB",
                # active mode: report every 1 sec
                # b"\xAA\xB4\x08\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x07\xAB"
                # active mode: report every 1 min
                # b"\xAA\xB4\x08\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x08\xAB"
                # ...
                # active mode: report every 30 min
                # b"\xAA\xB4\x08\x01\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x25\xAB"
                # firmware version
                # b"\xAA\xB4\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x05\xAB"
            },
        }[self.name][command]

    def answer_length(self, command: str) -> int:
        """Expected answer length to serial command"""
        length = self.Message.message_length
        return {
            "PMSx003": {
                "passive_mode": 8,
                "passive_read": length,
                "active_mode": length,
                "sleep": 8,
                "wake": length,
            }[command],
            "PMS3003": length,
            "SDS01x": length,
        }[self.name]

    @classmethod
    def guess(cls, buffer: bytes) -> "Sensor":
        """Guess sensor type from buffer contents"""
        if buffer[-8:] == b"\x42\x4D\x00\x04\xe1\x00\x01\x74":
            sensor = cls.PMSx003
        elif buffer[-10:-4] == b"\xAA\xC5\x02\x01\x01\x00":
            sensor = cls.SDS01x
        elif buffer:
            sensor = cls.PMS3003
        else:
            sensor = cls.PMSx003
            logger.debug(f"Sensor returned empty buffer, assume {sensor.name} on sleep mode")
        logger.debug(f"Guess {sensor.name} from buffer contents")
        return sensor

    def decode(self, buffer: bytes, *, time: Optional[int] = None) -> NamedTuple:
        """Decode a serial message"""
        if not time:
            time = self.Data.now()

        data = self.Message.decode(buffer)
        logger.debug(f"message data: {data}")

        return self.Data(time, *data[self.Message.data_records])
