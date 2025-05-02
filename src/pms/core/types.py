from datetime import datetime
from typing import Protocol


class Cmd(Protocol):
    """Single sensor command"""

    @property
    def command(self) -> bytes: ...

    @property
    def answer_header(self) -> bytes: ...

    @property
    def answer_length(self) -> int: ...


class Commands(Protocol):
    """Sensor commands"""

    @property
    def passive_read(self) -> Cmd: ...

    @property
    def passive_mode(self) -> Cmd: ...

    @property
    def active_mode(self) -> Cmd: ...

    @property
    def sleep(self) -> Cmd: ...

    @property
    def wake(self) -> Cmd: ...


class Message(Protocol):
    """Message from sensor"""

    @classmethod
    def decode(cls, message: bytes, command: Cmd) -> tuple[float, ...]: ...


class ObsData(Protocol):
    """Decoded sensor message"""

    def __init__(self, *data: float) -> None: ...

    @property
    def time(self) -> int: ...

    @property
    def date(self) -> datetime: ...

    def __format__(self, spec: str) -> str: ...

    def __str__(self): ...
