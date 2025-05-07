from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Protocol


class Cmd(NamedTuple):
    """Single sensor command"""

    command: bytes
    answer_header: bytes
    answer_length: int


class Commands(NamedTuple):
    """Required sensor commands"""

    passive_read: Cmd
    passive_mode: Cmd
    active_mode: Cmd
    sleep: Cmd
    wake: Cmd


class Message(Protocol):
    """Message from sensor"""

    @classmethod
    @abstractmethod
    def decode(cls, message: bytes, command: Cmd) -> tuple[int | float, ...]: ...


@dataclass
class ObsData(Protocol):
    """
    Decoded sensor message

    time: measurement time [seconds since epoch]
    date: measurement time [datetime object]
    """

    time: int

    @property
    def date(self) -> datetime:
        """measurement time as datetime object"""
        return datetime.fromtimestamp(self.time)

    @abstractmethod
    def __format__(self, spec: str) -> str: ...

    @abstractmethod
    def __str__(self): ...
