from __future__ import annotations

import warnings
from abc import abstractmethod
from dataclasses import asdict, dataclass
from typing import ClassVar

from loguru import logger

from pms import WrongMessageFormat
from pms.core.types import Cmd, Commands
from pms.core.types import Message as MessageProtocol
from pms.core.types import ObsData as ObsDataProtocol

__all__ = ["Cmd", "Commands", "Message", "ObsData"]


class Message(MessageProtocol):
    """BaseClass for serial messages from PM sensors"""

    data_records: ClassVar[slice]

    def __init__(self, message: bytes) -> None:
        logger.debug(f"message hex: {message.hex()}")
        self.message = message

    @classmethod
    def unpack(cls, message: bytes, header: bytes, length: int) -> tuple[float, ...]:
        try:
            # validate full message
            msg = cls._validate(message, header, length)
        except WrongMessageFormat:
            # search last complete message on buffer
            start = message.rfind(header, 0, len(header) - length)
            if start < 0:  # No match found
                raise
            # validate last complete message
            msg = cls._validate(message[start : start + length], header, length)

        # data: unpacked payload
        payload = cls._unpack(msg.payload)
        logger.debug(f"message payload: {payload}")
        return payload

    @classmethod
    def decode(cls, message: bytes, command: Cmd) -> tuple[float, ...]:
        header = command.answer_header
        length = command.answer_length
        return cls.unpack(message, header, length)[cls.data_records]

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
    def _validate(self, message: bytes, header: bytes, length: int) -> Message:
        pass

    @staticmethod
    @abstractmethod
    def _unpack(message: bytes) -> tuple[float, ...]:
        pass


@dataclass
class ObsData(ObsDataProtocol):
    """
    BaseClass for sensor measurements (decoded sensor messages)

    time: measurement time [seconds since epoch]
    date: measurement time [datetime object]
    """

    def subset(self, spec: str | None = None) -> dict[str, float]:  # pragma: no cover
        warnings.warn(
            "obs.subset is deprecated, use dataclasses.asdict(obs) for a dictionary mapping",
            DeprecationWarning,
            stacklevel=2,
        )
        if spec:
            obs = {k: v for k, v in asdict(self).items() if k.startswith(spec)}
        else:
            obs = {k: v for k, v in asdict(self).items() if k != "time"}
        if obs:
            return obs

        raise ValueError(
            f"Unknown subset code '{spec}' for object of type '{self.__class__.__qualname__}'"
        )

    @abstractmethod
    def __format__(self, spec: str) -> str:
        if spec == "header":  # header for csv file
            return ", ".join(asdict(self).keys())
        if spec == "":
            return str(self)

        raise ValueError(
            f"Unknown format code '{spec}' for object of type '{self.__class__.__qualname__}'"
        )

    def __str__(self):
        return self.__format__("pm")


def metadata(long_name: str, units: str, topic: str):
    """For fields(metadata=metadata(...))"""
    return dict(long_name=long_name, units=units, topic=topic)
