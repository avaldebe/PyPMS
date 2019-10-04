"""
Serial commands for Plantower sensors
- PMSx003 sensors support active/passive mode and sleep/wake
- PMS3003 sensors do not support commands
"""

from .base import Cmd, Commands


PMSx003 = Commands(
    passive_read=Cmd(b"\x42\x4D\xE2\x00\x00\x01\x71", b"\x42\x4D\x00\x1c", 32),
    passive_mode=Cmd(b"\x42\x4D\xE1\x00\x00\x01\x70", b"\x42\x4D\x00\x04", 8),
    active_mode=Cmd(b"\x42\x4D\xE1\x00\x01\x01\x71", b"\x42\x4D\x00\x1c", 32),
    sleep=Cmd(b"\x42\x4D\xE4\x00\x00\x01\x73", b"\x42\x4D\x00\x04", 8),
    wake=Cmd(b"\x42\x4D\xE4\x00\x01\x01\x74", b"\x42\x4D\x00\x1c", 32),
)


PMS3003 = Commands(
    passive_read=Cmd(b"", b"\x42\x4D\x00\x14", 24),
    passive_mode=Cmd(b"", b"\x42\x4D\x00\x14", 24),
    active_mode=Cmd(b"", b"\x42\x4D\x00\x14", 24),
    sleep=Cmd(b"", b"\x42\x4D\x00\x14", 24),
    wake=Cmd(b"", b"\x42\x4D\x00\x14", 24),
)
