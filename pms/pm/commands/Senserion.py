"""
Serial commands for Senserion sensors

- SPS30 protocol implements byte-stuffing
- There is no active mode read
"""

from .base import Cmd, Commands


SPS30 = Commands(
    # Read Measured Values
    passive_read=Cmd(b"\x7E\x00\x03\x00\xFC\x7E", b"\x7E\x00\x03\x00\x28", 47),
    passive_mode=Cmd(b"", b"", 0),
    active_mode=Cmd(b"", b"", 0),
    # Stop Measurement
    sleep=Cmd(b"\x7E\x00\x01\x00\xFE\x7E", b"\x7E\x00\x01\x00\x00", 7),
    # Start Measurement
    wake=Cmd(b"\x7E\x00\x00\x02\x01\x03\xF9\x7E", b"\x7E\x00\x00", 7),
)
