import os
import pytest

os.environ["LEVEL"] = "DEBUG"
from pms.sensor import pm
from pms import SensorWarning


@pytest.mark.parametrize(
    "sensor,hex,error",
    [
        pytest.param(
            pm.PMSx003, "424d001c0005000d0016", "message length: 10", id="PMSx003 short message"
        ),
        pytest.param(
            pm.PMSx003,
            "424d00000005000d00160005000d001602fd00fc001d000f00060006970003a9",
            r"message header: b'BM\x00\x00'",
            id="PMSx003 wrong header",
        ),
        pytest.param(
            pm.PMSx003,
            "424d001c0005000d00160005000d001602fd00fc001d000f0006000697000000",
            "message checksum 0 != 965",
            id="PMSx003 wrong checksum",
        ),
        pytest.param(
            pm.PMSx003,
            "424d001c000000000000000000000000000000000000000000000000000000ab",
            "message empty: warming up sensor",
            id="PMSx003 empty message",
        ),
        pytest.param(
            pm.PMS3003, "424d00140051006A0077", "message length: 10", id="PMS3003 short message"
        ),
        pytest.param(
            pm.PMS3003,
            "424d00000051006A007700350046004F33D20F28003F0406",
            r"message header: b'BM\x00\x00'",
            id="PMS3003 wrong header",
        ),
        pytest.param(
            pm.PMS3003,
            "424d00140051006A007700350046004F33D20F28003F0000",
            "message checksum 0 != 1050",
            id="PMS3003 wrong checksum",
        ),
        pytest.param(
            pm.PMS3003,
            "424d001400000000000000000000000000000000000000a3",
            "message empty: warming up sensor",
            id="PMS3003 empty message",
        ),
        pytest.param(pm.SDS01x, "AAC0D4041DAB", "message length: 6", id="SDS01x short message"),
        pytest.param(
            pm.SDS01x,
            "ABC0D4043A0AA1601DAA",
            r"message header: b'\xab\xc0'",
            id="SDS01x wrong header",
        ),
        pytest.param(
            pm.SDS01x, "AAC0D4043A0AA1601DAA", "message tail: 0xaa", id="SDS01x wrong tail"
        ),
        pytest.param(
            pm.SDS01x,
            "AAC0D4043A0AA16000AB",
            "message checksum 0 != 29",
            id="SDS01x wrong checksum",
        ),
        pytest.param(
            pm.SDS01x,
            "AAC000000000000000AB",
            "message empty: warming up sensor",
            id="SDS01x empty message",
        ),
        pytest.param(
            pm.SPS30, "7E00030028000000D47E", "message length: 10", id="SPS30 short message"
        ),
        pytest.param(
            pm.SPS30,
            "7E00030000FC7E",
            r"message header: b'~\x00\x03\x00\x00'",
            id="SPS30 wrong header",
        ),
        pytest.param(
            pm.SPS30,
            "7E0003002800000000000000000000000000000000000000000000000000000000000000000000000000000000D477",
            "message tail: 0x77",
            id="SPS30 wrong tail",
        ),
        pytest.param(
            pm.SPS30,
            "7E0003002800000000000000000000000000000000000000000000000000000000000000000000000000000000D07E",
            "message checksum 208 != 212",
            id="SPS30 wrong checksum",
        ),
        pytest.param(
            pm.SPS30,
            "7E0003002800000000000000000000000000000000000000000000000000000000000000000000000000000000D47E",
            "message empty: warming up sensor",
            id="SPS30 empty message",
        ),
    ],
)
def test_decode_error(sensor, hex, error):
    with pytest.raises(SensorWarning) as e:
        sensor.Message.decode(bytes.fromhex(hex), sensor.commands.passive_read)
    assert str(e.value) == error


@pytest.mark.parametrize(
    "message,header,length,error",
    [
        pytest.param(
            pm.PMSx003.Message,
            pm.PMSx003.commands.passive_read.answer_header[:3],
            pm.PMSx003.commands.passive_read.answer_length,
            "wrong header length 3",
            id="wrong header length",
        ),
        pytest.param(
            pm.PMSx003.Message,
            pm.PMSx003.commands.passive_read.answer_header * 2,
            pm.PMSx003.commands.passive_read.answer_length,
            "wrong header length 8",
            id="wrong header length",
        ),
        pytest.param(
            pm.PMSx003.Message,
            b"BN\x00\x1c",
            pm.PMSx003.commands.passive_read.answer_length,
            r"wrong header start b'BN\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            pm.PMSx003.Message,
            b"\x00\x1c\x00\x1c",
            pm.PMSx003.commands.passive_read.answer_length,
            r"wrong header start b'\x00\x1c\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            pm.PMSx003.Message,
            pm.PMSx003.commands.passive_read.answer_header,
            pm.PMS3003.commands.passive_read.answer_length,
            "wrong payload length 24",
            id="wrong payload length",
        ),
        pytest.param(
            pm.PMS3003.Message,
            pm.PMS3003.commands.passive_read.answer_header,
            pm.PMSx003.commands.passive_read.answer_length,
            "wrong payload length 32",
            id="wrong payload length",
        ),
        pytest.param(
            pm.SDS01x.Message,
            pm.SDS01x.commands.passive_read.answer_header[:1],
            pm.SDS01x.commands.passive_read.answer_length,
            "wrong header length 1",
            id="wrong header length",
        ),
        pytest.param(
            pm.SDS01x.Message,
            pm.SDS01x.commands.passive_read.answer_header * 2,
            pm.SDS01x.commands.passive_read.answer_length,
            "wrong header length 4",
            id="wrong header length",
        ),
        pytest.param(
            pm.SDS01x.Message,
            b"\x00\x1c",
            pm.SDS01x.commands.passive_read.answer_length,
            r"wrong header start b'\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            pm.SDS01x.Message,
            b"\x00\x1c",
            pm.SDS01x.commands.passive_read.answer_length,
            r"wrong header start b'\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            pm.SDS01x.Message,
            pm.SDS01x.commands.passive_read.answer_header,
            pm.PMSx003.commands.passive_read.answer_length,
            "wrong payload length 32",
            id="wrong payload length",
        ),
        pytest.param(
            pm.SDS01x.Message,
            pm.SDS01x.commands.passive_read.answer_header,
            pm.PMS3003.commands.passive_read.answer_length,
            "wrong payload length 24",
            id="wrong payload length",
        ),
    ],
)
def test_validate_error(message, header, length, error, buffer=b""):
    with pytest.raises(AssertionError) as e:
        message._validate(buffer, header, length)
    assert str(e.value) == error
