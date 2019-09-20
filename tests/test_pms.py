"""
Choose one of the following strategies

Run pytest as a module
$ python3 -m pytest test/

Install locally before testing
$ pip install -e .
$ pytest test/
"""
import os, time
import pytest

try:
    os.environ["LEVEL"] = "DEBUG"
    from pms import SensorData, SensorType
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize(
    "fmt", ["csv", "4csv", "04csv", "pm", "4pm", "04pm", "num", "4num", "04num"]
)
def test_format(fmt, raw=tuple(range(9)), secs=1567198523):
    obs = SensorData(secs, *raw)
    obs = f"{obs:{fmt}}"

    if fmt.endswith("csv"):
        secs = f"{secs},"
        fmt = "{:" + fmt[:-3] + "d}"
        raw = ", ".join(map(fmt.format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        fmt = "{:" + fmt[:-2] + "d}"
        raw = f"PM1 {fmt}, PM2.5 {fmt}, PM10 {fmt} ug/m3".format(*raw[:4])
    elif fmt.endswith("num"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        fmt = "{:" + fmt[:-3] + "d}"
        raw = (
            f"N0.3 {fmt}, N0.5 {fmt}, N1.0 {fmt}, "
            f"N2.5 {fmt}, N5.0 {fmt}, N10 {fmt} #/100cc"
        ).format(*raw[3:])

    assert obs == f"{secs} {raw}"


@pytest.mark.parametrize(
    "hex,msg",
    [
        pytest.param(
            "424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
            (5, 13, 22, 765, 252, 29, 15, 6, 6),
            id="known good data",
        ),
        pytest.param(
            "02fd00fc001d000f00060006970003c5424d001c0005000d00160005000d001602fd00fc001d000f00060006970003c5",
            (5, 13, 22, 765, 252, 29, 15, 6, 6),
            id="good data at the end of the buffer",
        ),
    ],
)
def test_decode(hex, msg, secs=1567201793, sensor=SensorType.PMSx003):
    assert sensor.decode(bytes.fromhex(hex), time=secs) == SensorData(secs, *msg)


@pytest.mark.parametrize(
    "hex,error",
    [
        pytest.param("424d001c0005000d00bd", "message length: 10", id="short message"),
        pytest.param(
            "424d00000005000d00160005000d001602fd00fc001d000f00060006970003a9",
            r"message header: b'BM\x00\x00'",
            id="wrong header",
        ),
        pytest.param(
            "424d001c0005000d00160005000d001602fd00fc001d000f0006000697000000",
            "message checksum 0 != 965",
            id="wrong checksum",
        ),
        pytest.param(
            "424d001c000000000000000000000000000000000000000000000000000000ab",
            "message empty: warming up sensor",
            id="empty message",
        ),
    ],
)
def test_decode_error(hex, error, secs=1567201793, sensor=SensorType.PMSx003):
    with pytest.raises(Exception) as e:
        sensor.decode(bytes.fromhex(hex), time=secs)
    assert str(e.value) == error
