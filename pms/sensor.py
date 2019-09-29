from enum import Enum
from typing import NamedTuple, Optional
from pms import logger
from .plantower import Message as PlantowerMessage, Data as PlantowerData
from .novafitness import Message as NovaFitnessMessage, Data as NovaFitnessData


class Sensor(Enum):
    """Supported PM sensors
    
    message signature: header, length
    - All SDS01x messages are 10b long;
    - PMS3003 messages are 24b long;
    - All other PMSx003 messages are 32b long;
    """

    PMSx003 = (b"\x42\x4D\x00\x1c", 32, PlantowerMessage, PlantowerData)
    PMS1003 = PMS5003 = PMS7003 = PMSA003 = PMSx003
    PMS3003 = (b"\x42\x4D\x00\x14", 24, PlantowerMessage, PlantowerData)
    Default = PMSx003
    G1 = PMS1003
    G3 = PMS3003
    G5 = PMS5003
    G7 = PMS7003
    G10 = PMSA003
    SDS01x = (b"\xAA\xC0", 10, NovaFitnessMessage, NovaFitnessData)
    SDS011 = SDS018 = SDS01x

    @property
    def message_header(self) -> bytes:
        return self.value[0]

    @property
    def message_length(self) -> int:
        return self.value[1]

    @property
    def Message(self):
        return self.value[2]

    @property
    def Data(self):
        return self.value[3]

    @property
    def message_records(self) -> int:
        """Data records in message"""
        return {"PMS3003": 6, "PMSx003": 12, "SDS01x": 2}[self.name]

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
        return {
            "PMSx003": {
                "passive_mode": 8,
                "passive_read": self.message_length,
                "active_mode": self.message_length,
                "sleep": 8,
                "wake": self.message_length,
            }[command],
            "PMS3003": self.message_length,
            "SDS01x": self.message_length,
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
            logger.debug(
                f"Sensor returned empty buffer, assume {sensor.name} on sleep mode"
            )
        logger.debug(f"Guess {sensor.name}, #{sensor.message_length}b message")
        return sensor

    def decode(self, buffer: bytes, *, time: Optional[int] = None) -> NamedTuple:
        """Decode a serial message"""
        if not time:
            time = self.Data.now()

        data = self.Message.decode(buffer, self.message_header, self.message_length)
        logger.debug(f"message data: {data}")

        return self.Data(time, *data[: self.message_records])
