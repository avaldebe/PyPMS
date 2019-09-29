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
    from pms.plantower import Data as SensorData
    from pms.sensor import Sensor
    from pms import SensorWarning
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize("fmt", "csv 4csv 04csv pm 4pm 04pm num 4num 04num cf .2cf 4.2cf".split())
def test_format(fmt, raw=tuple(range(1, 13)), secs=1567198523):
    obs = SensorData(secs, *raw)
    obs = f"{obs:{fmt}}"

    if fmt.endswith("csv"):
        secs = f"{secs},"
        fmt = "{:" + fmt[:-3] + "d}"
        raw = ", ".join(map(fmt.format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        fmt = "{:" + fmt[:-2] + "d}"
        raw = f"PM1 {fmt}, PM2.5 {fmt}, PM10 {fmt} ug/m3".format(*raw[3:6])
    elif fmt.endswith("num"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        fmt = "{:" + fmt[:-3] + "d}"
        raw = (
            f"N0.3 {fmt}, N0.5 {fmt}, N1.0 {fmt}, " f"N2.5 {fmt}, N5.0 {fmt}, N10 {fmt} #/100cc"
        ).format(*raw[6:])
    elif fmt.endswith("cf"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        fmt = "{:" + (fmt[:-2] or ".0") + "%}"
        raw = f"CF1 {fmt}, CF2.5 {fmt}, CF10 {fmt}".format(
            raw[3] / raw[0], raw[4] / raw[1], raw[5] / raw[2]
        )

    assert obs == f"{secs} {raw}"
