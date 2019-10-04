from typing import NamedTuple


class Cmd(NamedTuple):
    command: bytes
    answer_header: bytes
    answer_length: int


class Commands(NamedTuple):
    passive_read: Cmd
    passive_mode: Cmd
    active_mode: Cmd
    sleep: Cmd
    wake: Cmd
