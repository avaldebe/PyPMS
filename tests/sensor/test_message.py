import pytest

from pms import SensorWarning
from pms.sensors.bosch_sensortec import mcu680
from pms.sensors.honeywell import hpma115s0
from pms.sensors.novafitness import sds01x
from pms.sensors.plantower import pms3003, pmsx003
from pms.sensors.sensirion import sps30
from pms.sensors.winsen import mhz19b


@pytest.mark.parametrize(
    "sensor,hex,error",
    [
        pytest.param(
            pmsx003, "424d001c0005000d0016", "message length: 10", id="PMSx003 short message"
        ),
        pytest.param(
            pmsx003,
            "424d00000005000d00160005000d001602fd00fc001d000f00060006970003a9",
            r"message header: b'BM\x00\x00'",
            id="PMSx003 wrong header",
        ),
        pytest.param(
            pmsx003,
            "424d001c0005000d00160005000d001602fd00fc001d000f0006000697000000",
            "message checksum 0 != 965",
            id="PMSx003 wrong checksum",
        ),
        pytest.param(
            pmsx003,
            "424d001c000000000000000000000000000000000000000000000000000000ab",
            "message empty: warming up sensor",
            id="PMSx003 empty message",
        ),
        pytest.param(
            pms3003, "424d00140051006A0077", "message length: 10", id="PMS3003 short message"
        ),
        pytest.param(
            pms3003,
            "424d00000051006A007700350046004F33D20F28003F0406",
            r"message header: b'BM\x00\x00'",
            id="PMS3003 wrong header",
        ),
        pytest.param(
            pms3003,
            "424d00140051006A007700350046004F33D20F28003F0000",
            "message checksum 0 != 1050",
            id="PMS3003 wrong checksum",
        ),
        pytest.param(
            pms3003,
            "424d001400000000000000000000000000000000000000a3",
            "message empty: warming up sensor",
            id="PMS3003 empty message",
        ),
        pytest.param(sds01x, "AAC0D4041DAB", "message length: 6", id="SDS01x short message"),
        pytest.param(
            sds01x,
            "ABC0D4043A0AA1601DAA",
            r"message header: b'\xab\xc0'",
            id="SDS01x wrong header",
        ),
        pytest.param(sds01x, "AAC0D4043A0AA1601DAA", "message tail: 0xaa", id="SDS01x wrong tail"),
        pytest.param(
            sds01x,
            "AAC0D4043A0AA16000AB",
            "message checksum 0 != 29",
            id="SDS01x wrong checksum",
        ),
        pytest.param(
            sds01x,
            "AAC000000000000000AB",
            "message empty: warming up sensor",
            id="SDS01x empty message",
        ),
        pytest.param(
            hpma115s0,
            "7E00030000FC7E",
            r"message header: b'~\x00\x03'",
            id="HPMA115S0 wrong header",
        ),
        pytest.param(
            hpma115s0, "400504303156", "message length: 6 != 8", id="HPMA115S0 short message"
        ),
        pytest.param(
            hpma115s0,
            "4005040030003100",
            "message checksum 0 != 86",
            id="HPMA115S0 wrong checksum",
        ),
        pytest.param(
            hpma115s0,
            "40050400000000B7",
            "message empty: warming up sensor",
            id="HPMA115S0 empty message",
        ),
        pytest.param(
            sps30, "7E00030028000000D47E", "message length: 10 != 47", id="SPS30 short message"
        ),
        pytest.param(
            sps30,
            "7E00000000FF7E",
            r"message header: b'~\x00\x00\x00\x00'",
            id="SPS30 wrong header",
        ),
        pytest.param(
            sps30,
            "7E0003002800000000000000000000000000000000000000000000000000000000000000000000000000000000D477",
            "message tail: 0x77",
            id="SPS30 wrong tail",
        ),
        pytest.param(
            sps30,
            "7E0003002800000000000000000000000000000000000000000000000000000000000000000000000000000000D07E",
            "message checksum 208 != 212",
            id="SPS30 wrong checksum",
        ),
        pytest.param(
            sps30,
            "7E0003002800000000000000000000000000000000000000000000000000000000000000000000000000000000D47E",
            "message empty: warming up sensor",
            id="SPS30 empty message",
        ),
        pytest.param(
            sps30,
            "7E00000000FF7E7E00004300BC7E",
            "short message: command not allowed in current state",
            id="SPS30 command not allowed",
        ),
        pytest.param(
            sps30,
            "7E00000000FF7E7E00030000FC7E",
            "short message: no data",
            id="SPS30 no data",
        ),
        pytest.param(
            mcu680, "5A5A3F0F0835198A0188", "message length: 10", id="MCU680 short message"
        ),
        pytest.param(
            mcu680,
            "5A5A00000835198A01885430D200032BE1004A1A",
            r"message header: b'ZZ\x00\x00'",
            id="MCU680 wrong header",
        ),
        pytest.param(
            mcu680,
            "5A5A3F0F0835198A01885430D200032BE1004A00",
            "message checksum 0 != 26",
            id="MCU680 wrong checksum",
        ),
        pytest.param(
            mcu680,
            "5A5A3F0F00000000000000000000000000000002",
            "message empty: warming up sensor",
            id="MCU680 empty message",
        ),
        pytest.param(mhz19b, "FF8601F4", "message length: 4", id="MHZ19B short message"),
        pytest.param(
            mhz19b, "FF8701F40000000084", r"message header: b'\xff\x87'", id="MHZ19B wrong header"
        ),
        pytest.param(
            mhz19b,
            "FF8601F40000000084",
            "message checksum 0x85 != 0x84",
            id="MHZ19B wrong checksum",
        ),
        pytest.param(
            mhz19b,
            "FF860000000000007A",
            "message empty: warming up sensor",
            id="MHZ19B wrong checksum",
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
            pmsx003.Message,
            pmsx003.commands.passive_read.answer_header[:3],
            pmsx003.commands.passive_read.answer_length,
            "wrong header length 3",
            id="PMSx003 wrong header length",
        ),
        pytest.param(
            pmsx003.Message,
            pmsx003.commands.passive_read.answer_header * 2,
            pmsx003.commands.passive_read.answer_length,
            "wrong header length 8",
            id="PMSx003 wrong header length",
        ),
        pytest.param(
            pmsx003.Message,
            b"BN\x00\x1c",
            pmsx003.commands.passive_read.answer_length,
            r"wrong header start b'BN\x00\x1c'",
            id="PMSx003 wrong header start",
        ),
        pytest.param(
            pmsx003.Message,
            b"\x00\x1c\x00\x1c",
            pmsx003.commands.passive_read.answer_length,
            r"wrong header start b'\x00\x1c\x00\x1c'",
            id="PMSx003 wrong header start",
        ),
        pytest.param(
            pmsx003.Message,
            pmsx003.commands.passive_read.answer_header,
            pms3003.commands.passive_read.answer_length,
            "wrong payload length 24 != 32",
            id="PMSx003 wrong payload length",
        ),
        pytest.param(
            pms3003.Message,
            pms3003.commands.passive_read.answer_header,
            pmsx003.commands.passive_read.answer_length,
            "wrong payload length 32 != 24",
            id="PMS3003 wrong payload length",
        ),
        pytest.param(
            sds01x.Message,
            sds01x.commands.passive_read.answer_header[:1],
            sds01x.commands.passive_read.answer_length,
            "wrong header length 1",
            id="SDS01x wrong header length",
        ),
        pytest.param(
            sds01x.Message,
            sds01x.commands.passive_read.answer_header * 2,
            sds01x.commands.passive_read.answer_length,
            "wrong header length 4",
            id="SDS01x wrong header length",
        ),
        pytest.param(
            sds01x.Message,
            b"\x00\x1c",
            sds01x.commands.passive_read.answer_length,
            r"wrong header start b'\x00\x1c'",
            id="SDS01x wrong header start",
        ),
        pytest.param(
            sds01x.Message,
            sds01x.commands.passive_read.answer_header,
            pmsx003.commands.passive_read.answer_length,
            "wrong payload length 32 != 10",
            id="SDS01x wrong payload length",
        ),
        pytest.param(
            sds01x.Message,
            sds01x.commands.passive_read.answer_header,
            pms3003.commands.passive_read.answer_length,
            "wrong payload length 24 != 10",
            id="SDS01x wrong payload length",
        ),
        pytest.param(
            sps30.Message,
            sps30.commands.passive_read.answer_header[:1],
            sps30.commands.passive_read.answer_length,
            "wrong header length 1",
            id="SPS30 wrong header length",
        ),
        pytest.param(
            sps30.Message,
            sps30.commands.passive_read.answer_header * 2,
            sps30.commands.passive_read.answer_length,
            "wrong header length 10",
            id="SPS30 wrong header length",
        ),
        pytest.param(
            sps30.Message,
            b"\x7E\x01\x00\x00\x00",
            sps30.commands.passive_read.answer_length,
            r"wrong header start b'~\x01\x00\x00\x00'",
            id="SPS30 wrong header start",
        ),
        pytest.param(
            sps30.Message,
            sps30.commands.passive_read.answer_header,
            pmsx003.commands.passive_read.answer_length,
            "wrong payload length 32 != 4||47",
            id="SPS30 wrong payload length",
        ),
    ],
)
def test_validate_error(message, header, length, error, buffer=b""):
    with pytest.raises(AssertionError) as e:
        message._validate(buffer, header, length)
    assert str(e.value) == error
