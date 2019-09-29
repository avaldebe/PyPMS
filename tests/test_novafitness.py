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
    from pms.novafitness import Data as SensorData, Message as SensorMessage
    from pms.sensor import Sensor
    from pms import SensorWarning
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize("fmt", "csv .2csv 4.2csv pm .2pm 4.2pm".split())
def test_format(fmt, raw=(12, 13), secs=1567198523):
    obs = SensorData(secs, *raw)
    obs = f"{obs:{fmt}}"

    raw = tuple(r / 10 for r in raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        fmt = "{:" + (fmt[:-3] or ".1") + "f}"
        raw = ", ".join(map(fmt.format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        fmt = "{:" + (fmt[:-2] or "0.1") + "f}"
        raw = f"PM2.5 {fmt}, PM10 {fmt} ug/m3".format(*raw)

    assert obs == f"{secs} {raw}"


@pytest.mark.parametrize(
    "header,length,error",
    [
        pytest.param(
            Sensor.SDS011.message_header[:1],
            Sensor.SDS011.message_length,
            "wrong header length 1",
            id="wrong header length",
        ),
        pytest.param(
            Sensor.SDS011.message_header * 2,
            Sensor.SDS011.message_length,
            "wrong header length 4",
            id="wrong header length",
        ),
        pytest.param(
            b"\x00\x1c",
            Sensor.SDS011.message_length,
            r"wrong header start b'\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            b"\x00\x1c",
            Sensor.SDS011.message_length,
            r"wrong header start b'\x00\x1c'",
            id="wrong header start",
        ),
        pytest.param(
            Sensor.SDS011.message_header,
            Sensor.PMSx003.message_length,
            "wrong payload length 32",
            id="wrong payload length",
        ),
        pytest.param(
            Sensor.SDS011.message_header,
            Sensor.PMS3003.message_length,
            "wrong payload length 24",
            id="wrong payload length",
        ),
    ],
)
def test_validate_error(
    header,
    length,
    error,
    message=bytes.fromhex(
        "AAC0D4043A0AA1601DAB"
    ),
):
    with pytest.raises(AssertionError) as e:
        SensorMessage._validate(message, header, length)
    assert str(e.value) == error
