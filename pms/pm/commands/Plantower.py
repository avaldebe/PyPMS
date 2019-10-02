"""
Serial commands for Plantower sensors
- PMSx003 sensors support active/passive mode and sleep/wake
- PMS3003 sensors do not support commands
"""

from typing import Tuple
from .base import BaseCmd
from .. import message


class PMSx003(BaseCmd):
    """Plantower PMSx003 commands"""

    passive_mode = (b"\x42\x4D\xE1\x00\x00\x01\x70", 8)
    passive_read = (b"\x42\x4D\xE2\x00\x00\x01\x71", message.PMSx003.message_length)
    active_mode = (b"\x42\x4D\xE1\x00\x01\x01\x71", message.PMSx003.message_length)
    sleep = (b"\x42\x4D\xE4\x00\x00\x01\x73", 8)
    wake = (b"\x42\x4D\xE4\x00\x01\x01\x74", message.PMSx003.message_length)


class PMS3003(BaseCmd):
    """Plantower PMS3003 commands"""

    active_read = (b"", message.PMS3003.message_length)
    passive_read = passive_mode = active_mode = sleep = wake = active_read
