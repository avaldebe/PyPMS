from enum import Enum
from typing import NamedTuple


class Cmd(NamedTuple):
    command: bytes
    answer_length: int


class BaseCmd(Enum):
    def __init__(self, command: bytes, answer_length: int):
        self.command: bytes = command
        self.answer_length: int = answer_length
