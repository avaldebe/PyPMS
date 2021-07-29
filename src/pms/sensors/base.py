import warnings
from abc import ABCMeta, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, NamedTuple, Tuple

from pms import WrongMessageFormat, logger


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
    def decode(cls, message: bytes, command: Cmd) -> Tuple[float, ...]:
        header = command.answer_header
        length = command.answer_length
        return cls.unpack(message, header, length)[cls.data_records]  # type: ignore[call-overload]

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


@dataclass  # type: ignore[misc]
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

    def subset(self, spec: str = None) -> Dict[str, float]:  # pragma: no cover
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
