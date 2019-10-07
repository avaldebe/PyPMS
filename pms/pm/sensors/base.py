from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import NamedTuple, Tuple, Dict
from datetime import datetime
from pms import logger, WrongMessageFormat


class Cmd(NamedTuple):
    """Single command"""

    command: bytes
    answer_header: bytes
    answer_length: int


class Commands(NamedTuple):
    """Required commands"""

    passive_read: Cmd
    passive_mode: Cmd
    active_mode: Cmd
    sleep: Cmd
    wake: Cmd


class Message(metaclass=ABCMeta):
    """
    Base class for serial messages from PM sensors
    """

    def __init__(self, message: bytes) -> None:
        logger.debug(f"message hex: {message.hex()}")
        self.message = message

    @classmethod
    def unpack(cls, message: bytes, header: bytes, length: int) -> Tuple[float, ...]:
        try:
            # validate full message
            msg = cls._validate(message, header, length)
        except WrongMessageFormat as e:
            # search last complete message on buffer
            start = message.rfind(header, 0, 4 - length)
            if start < 0:  # No match found
                raise
            # validate last complete message
            msg = cls._validate(message[start : start + length], header, length)

        # data: unpacked payload
        payload = cls._unpack(msg.payload)
        logger.debug(f"message payload: {payload}")
        return payload

    @classmethod
    def decode(cls, message: bytes, command: Cmd) -> Tuple[float, ...]:
        header = command.answer_header
        length = command.answer_length
        return cls.unpack(message, header, length)[cls.data_records]  # type: ignore

    @property
    @classmethod
    @abstractmethod
    def data_records(cls) -> slice:
        pass

    @property
    @abstractmethod
    def header(self) -> bytes:
        pass

    @property
    @abstractmethod
    def payload(self) -> bytes:
        pass

    @property
    @abstractmethod
    def checksum(self) -> int:
        pass

    @classmethod
    @abstractmethod
    def _validate(self, message: bytes, header: bytes, length: int) -> "Message":
        pass

    @staticmethod
    @abstractmethod
    def _unpack(message: bytes) -> Tuple[float, ...]:
        pass


@dataclass  # type: ignore
class ObsData(metaclass=ABCMeta):
    """Measurements
    
    time: measurement time [seconds since epoch]
    date: measurement time [datetime object]
    """

    time: int

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    @abstractmethod
    def subset(self, spec: str) -> Dict[str, float]:
        pass

    @abstractmethod
    def __format__(self, spec: str) -> str:
        pass

    def __str__(self):
        return self.__format__("pm")
