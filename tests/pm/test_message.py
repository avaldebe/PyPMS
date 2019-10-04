"""
Choose one of the following strategies

Run pytest as a module
$ python3 -m pytest test/

Install locally before testing
$ pip install -e .
$ pytest test/
"""
import os
import pytest

try:
    os.environ["LEVEL"] = "DEBUG"
    from pms.pm import message, commands
    from pms import SensorWarning
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize(
    "message,command,hex,error",
    [
        pytest.param(
            message.PMSx003,
            commands.PMSx003.passive_read,
            "424d001c0005000d0016",
            "message length: 10",
            id="short message",
        ),
        pytest.param(
            message.PMSx003,
            commands.PMSx003.passive_read,
            "424d00000005000d00160005000d001602fd00fc001d000f00060006970003a9",
            r"message header: b'BM\x00\x00'",
            id="wrong header",
        ),
        pytest.param(
            message.PMSx003,
            commands.PMSx003.passive_read,
            "424d001c0005000d00160005000d001602fd00fc001d000f0006000697000000",
            "message checksum 0 != 965",
            id="wrong checksum",
        ),
        pytest.param(
            message.PMSx003,
            commands.PMSx003.passive_read,
            "424d001c000000000000000000000000000000000000000000000000000000ab",
            "message empty: warming up sensor",
            id="empty message",
        ),
        pytest.param(
            message.PMS3003,
            commands.PMS3003.passive_read,
            "424d00140051006A0077",
            "message length: 10",
            id="short message",
        ),
        pytest.param(
            message.PMS3003,
            commands.PMS3003.passive_read,
            "424d00000051006A007700350046004F33D20F28003F0406",
            r"message header: b'BM\x00\x00'",
            id="wrong header",
        ),
        pytest.param(
            message.PMS3003,
            commands.PMS3003.passive_read,
            "424d00140051006A007700350046004F33D20F28003F0000",
            "message checksum 0 != 1050",
            id="wrong checksum",
        ),
        pytest.param(
            message.PMS3003,
            commands.PMS3003.passive_read,
            "424d001400000000000000000000000000000000000000a3",
            "message empty: warming up sensor",
            id="empty message",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read,
            "AAC0D4041DAB",
            "message length: 6",
            id="short message",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read,
            "ABC0D4043A0AA1601DAA",
            r"message header: b'\xab\xc0'",
            id="wrong header",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read,
            "AAC0D4043A0AA1601DAA",
            "message tail: 0xaa",
            id="wrong tail",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read,
            "AAC0D4043A0AA16000AB",
            "message checksum 0 != 29",
            id="wrong checksum",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read,
            "AAC000000000000000AB",
            "message empty: warming up sensor",
            id="empty message",
        ),
    ],
)
def test_decode_error(message, command, hex, error):
    with pytest.raises(SensorWarning) as e:
        message.decode(bytes.fromhex(hex), command)
    assert str(e.value) == error


@pytest.mark.parametrize(
    "message,header,length,error",
    [
        pytest.param(
            message.PMSx003,
            commands.PMSx003.passive_read.answer_header[:3],
            commands.PMSx003.passive_read.answer_length,
            "wrong header length 3",
            id="wrong header length",
        ),
        pytest.param(
            message.PMSx003,
            commands.PMSx003.passive_read.answer_header * 2,
            commands.PMSx003.passive_read.answer_length,
            "wrong header length 8",
            id="wrong header length",
        ),
        pytest.param(
            message.PMSx003,
            b"BN\x00\x1c",
            commands.PMSx003.passive_read.answer_length,
            r"wrong header start b'BN\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            message.PMSx003,
            b"\x00\x1c\x00\x1c",
            commands.PMSx003.passive_read.answer_length,
            r"wrong header start b'\x00\x1c\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            message.PMSx003,
            commands.PMSx003.passive_read.answer_header,
            commands.PMS3003.passive_read.answer_length,
            "wrong payload length 24",
            id="wrong payload length",
        ),
        pytest.param(
            message.PMS3003,
            commands.PMS3003.passive_read.answer_header,
            commands.PMSx003.passive_read.answer_length,
            "wrong payload length 32",
            id="wrong payload length",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read.answer_header[:1],
            commands.SDS01x.passive_read.answer_length,
            "wrong header length 1",
            id="wrong header length",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read.answer_header * 2,
            commands.SDS01x.passive_read.answer_length,
            "wrong header length 4",
            id="wrong header length",
        ),
        pytest.param(
            message.SDS01x,
            b"\x00\x1c",
            commands.SDS01x.passive_read.answer_length,
            r"wrong header start b'\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            message.SDS01x,
            b"\x00\x1c",
            commands.SDS01x.passive_read.answer_length,
            r"wrong header start b'\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read.answer_header,
            commands.PMSx003.passive_read.answer_length,
            "wrong payload length 32",
            id="wrong payload length",
        ),
        pytest.param(
            message.SDS01x,
            commands.SDS01x.passive_read.answer_header,
            commands.PMS3003.passive_read.answer_length,
            "wrong payload length 24",
            id="wrong payload length",
        ),
    ],
)
def test_validate_error(message, header, length, error, buffer=b""):
    with pytest.raises(AssertionError) as e:
        message._validate(buffer, header, length)
    assert str(e.value) == error
