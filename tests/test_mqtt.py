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
    from pms.mqtt import SensorData
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize(
    "location,measurement,value",
    [("test", "pm01", 5), ("test", "pm25", 10), ("test", "pm10", 27)],
)
def test_decode(location, measurement, value, secs=1567201793):
    assert SensorData(secs, location, measurement, value) == SensorData.decode(
        f"homie/{location}/{measurement}/concentration", f"{value:.2f}", time=secs
    )


@pytest.mark.parametrize(
    "topic,payload,error",
    [
        ("short/topic", "27.00", "topic total length: 2"),
        ("too/long/topic/+/+/+", "27.00", "topic total length: 6"),
        ("sneaky/system/topic/$+", "27.00", "system topic: sneaky/system/topic/$+"),
        ("other/$system/topic/+", "27.00", "system topic: other/$system/topic/+"),
        ("non/numeric/payload/+", "OK", "non numeric payload: OK"),
        ("non/numeric/payload/+", "value27", "non numeric payload: value27"),
        ("non/numeric/payload/+", "27,00", "non numeric payload: 27,00"),
    ],
)
def test_decode_error(topic, payload, error, secs=1567201793):
    with pytest.raises(Exception) as e:
        SensorData.decode(topic, payload, time=secs)
    assert str(e.value) == error
