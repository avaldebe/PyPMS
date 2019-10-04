"""
Base class for serial messages from PM sensors
"""

from abc import ABC, abstractmethod
from typing import Tuple
from pms import logger, WrongMessageFormat
from .. import commands


class Message(ABC):
    def __init__(self, message: bytes) -> None:
        logger.debug(f"message hex: {message.hex()}")
        self.message = message

    @classmethod
    def unpack(cls, message: bytes, header: bytes, length: int) -> Tuple[int, ...]:
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
    def decode(cls, message: bytes, command: commands.Cmd) -> Tuple[int, ...]:
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
    def _unpack(message: bytes) -> Tuple[int, ...]:
        pass
