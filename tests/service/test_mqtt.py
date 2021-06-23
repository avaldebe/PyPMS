import pytest

from pms import logger
from pypms.extra import mqtt

logger.setLevel("DEBUG")


@pytest.mark.parametrize(
    "location,measurement,value",
    [
        pytest.param("test", "pm01", 5, id="pm01"),
        pytest.param("test", "pm25", 10, id="pm25"),
        pytest.param("test", "pm10", 27, id="pm10"),
    ],
)
def test_decode(location, measurement, value, secs=1_567_201_793):
    assert mqtt.Data(secs, location, measurement, value) == mqtt.Data.decode(
        f"homie/{location}/{measurement}/concentration", f"{value:.2f}", time=secs
    )


@pytest.mark.parametrize(
    "topic,payload,error",
    [
        pytest.param("short/topic", "27.00", "topic total length: 2", id="short topic"),
        pytest.param("too/long/topic/+/+/+", "27.00", "topic total length: 6", id="long topic"),
        pytest.param(
            "sneaky/system/topic/$+",
            "27.00",
            "system topic: sneaky/system/topic/$+",
            id="system topic",
        ),
        pytest.param(
            "other/$system/topic/+",
            "27.00",
            "system topic: other/$system/topic/+",
            id="system topic",
        ),
        pytest.param("non/numeric/payload/+", "OK", "non numeric payload: OK", id="NaN payload"),
        pytest.param(
            "non/numeric/payload/+", "value27", "non numeric payload: value27", id="NaN payload"
        ),
        pytest.param(
            "non/numeric/payload/+", "27,00", "non numeric payload: 27,00", id="NaN payload"
        ),
    ],
)
def test_decode_error(topic, payload, error, secs=1_567_201_793):
    with pytest.raises(Exception) as e:
        mqtt.Data.decode(topic, payload, time=secs)
    assert str(e.value) == error
