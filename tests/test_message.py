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
    from pms.message import PMSx003, PMS3003, SDS01x
    from pms import SensorWarning
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize(
    "sensor,hex,error",
    [
        pytest.param(PMSx003, "424d001c0005000d0016", "message length: 10", id="short message"),
        pytest.param(
            PMSx003,
            "424d00000005000d00160005000d001602fd00fc001d000f00060006970003a9",
            r"message header: b'BM\x00\x00'",
            id="wrong header",
        ),
        pytest.param(
            PMSx003,
            "424d001c0005000d00160005000d001602fd00fc001d000f0006000697000000",
            "message checksum 0 != 965",
            id="wrong checksum",
        ),
        pytest.param(
            PMSx003,
            "424d001c000000000000000000000000000000000000000000000000000000ab",
            "message empty: warming up sensor",
            id="empty message",
        ),
        pytest.param(PMS3003, "424d00140051006A0077", "message length: 10", id="short message"),
        pytest.param(
            PMS3003,
            "424d00000051006A007700350046004F33D20F28003F0406",
            r"message header: b'BM\x00\x00'",
            id="wrong header",
        ),
        pytest.param(
            PMS3003,
            "424d00140051006A007700350046004F33D20F28003F0000",
            "message checksum 0 != 1050",
            id="wrong checksum",
        ),
        pytest.param(
            PMS3003,
            "424d001400000000000000000000000000000000000000a3",
            "message empty: warming up sensor",
            id="empty message",
        ),
        pytest.param(SDS01x, "AAC0D4041DAB", "message length: 6", id="short message"),
        pytest.param(
            SDS01x, "ABC0D4043A0AA1601DAA", r"message header: b'\xab\xc0'", id="wrong header"
        ),
        pytest.param(SDS01x, "AAC0D4043A0AA1601DAA", "message tail: 0xaa", id="wrong tail"),
        pytest.param(
            SDS01x, "AAC0D4043A0AA16000AB", "message checksum 0 != 29", id="wrong checksum"
        ),
        pytest.param(
            SDS01x, "AAC000000000000000AB", "message empty: warming up sensor", id="empty message"
        ),
    ],
)
def test_decode_error(sensor, hex, error):
    with pytest.raises(SensorWarning) as e:
        sensor.decode(bytes.fromhex(hex))
    assert str(e.value) == error


@pytest.mark.parametrize(
    "sensor,header,length,error",
    [
        pytest.param(
            PMSx003,
            PMSx003.message_header[:3],
            PMSx003.message_length,
            "wrong header length 3",
            id="wrong header length",
        ),
        pytest.param(
            PMSx003,
            PMSx003.message_header * 2,
            PMSx003.message_length,
            "wrong header length 8",
            id="wrong header length",
        ),
        pytest.param(
            PMSx003,
            b"BN\x00\x1c",
            PMSx003.message_length,
            r"wrong header start b'BN\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            PMSx003,
            b"\x00\x1c\x00\x1c",
            PMSx003.message_length,
            r"wrong header start b'\x00\x1c\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            PMSx003,
            PMSx003.message_header,
            PMS3003.message_length,
            "wrong payload length 24",
            id="wrong payload length",
        ),
        pytest.param(
            PMS3003,
            PMS3003.message_header,
            PMSx003.message_length,
            "wrong payload length 32",
            id="wrong payload length",
        ),
        pytest.param(
            SDS01x,
            SDS01x.message_header[:1],
            SDS01x.message_length,
            "wrong header length 1",
            id="wrong header length",
        ),
        pytest.param(
            SDS01x,
            SDS01x.message_header * 2,
            SDS01x.message_length,
            "wrong header length 4",
            id="wrong header length",
        ),
        pytest.param(
            SDS01x,
            b"\x00\x1c",
            SDS01x.message_length,
            r"wrong header start b'\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            SDS01x,
            b"\x00\x1c",
            SDS01x.message_length,
            r"wrong header start b'\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            SDS01x,
            SDS01x.message_header,
            PMSx003.message_length,
            "wrong payload length 32",
            id="wrong payload length",
        ),
        pytest.param(
            SDS01x,
            SDS01x.message_header,
            PMS3003.message_length,
            "wrong payload length 24",
            id="wrong payload length",
        ),
    ],
)
def test_validate_error(sensor, header, length, error, message=b""):
    with pytest.raises(AssertionError) as e:
        sensor._validate(message, header, length)
    assert str(e.value) == error
