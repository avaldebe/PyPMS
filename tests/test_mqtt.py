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
    from pms.mqtt import SensorData
except ModuleNotFoundError as e:
    print(__doc__)
    raise


def test_decode():
    sec = 1567201793
    location, measurement, value = "test", "pm10", 27
    topic = f"homie/{location}/{measurement}/concentration"
    payload = f"{value:.2f}"

    assert SensorData.decode(topic, payload, time=sec) == SensorData(
        sec, location, measurement, value
    ), "decode: known good data"

    with pytest.raises(Exception) as e:
        topic = "short/topic"
        SensorData.decode(topic, payload, time=sec)
    assert str(e.value) == "topic total length: 2"

    with pytest.raises(Exception) as e:
        topic = "too/long/topic/+/+/+"
        SensorData.decode(topic, payload, time=sec)
    assert str(e.value) == "topic total length: 6"

    with pytest.raises(Exception) as e:
        topic = "sneaky/system/topic/$online"
        SensorData.decode(topic, payload, time=sec)
    assert str(e.value) == f"system topic: {topic}"

    with pytest.raises(Exception) as e:
        topic = "non/numeric/payload/status"
        payload = "ok"
        SensorData.decode(topic, payload, time=sec)
    assert str(e.value) == f"non numeric payload: {payload}"

