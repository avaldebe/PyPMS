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
    from pms.pm.obsdata import PMSx003, SDS01x
    from pms import SensorWarning
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize(
    "fmt,sensor",
    [(fmt, PMSx003) for fmt in "csv 4csv 04csv pm 4pm 04pm num 4num 04num cf .2cf 4.2cf".split()]
    + [(fmt, SDS01x) for fmt in "csv .2csv 4.2csv pm .2pm 4.2pm".split()],  # type: ignore
)
def test_format(fmt, sensor, raw=tuple(range(1, 13)), secs=1567198523):

    if sensor is PMSx003:
        obs = sensor(secs, *raw)
        if fmt.endswith("csv"):
            secs = f"{secs},"
            f = "{:" + fmt[:-3] + "d}"
            raw = ", ".join(map(f.format, raw))
        elif fmt.endswith("pm"):
            secs = time.strftime("%F %T:", time.localtime(secs))
            f = "{:" + fmt[:-2] + "d}"
            raw = f"PM1 {f}, PM2.5 {f}, PM10 {f} ug/m3".format(*raw[3:6])
        elif fmt.endswith("num"):
            secs = time.strftime("%F %T:", time.localtime(secs))
            f = "{:" + fmt[:-3] + "d}"
            raw = (f"N0.3 {f}, N0.5 {f}, N1.0 {f}, " f"N2.5 {f}, N5.0 {f}, N10 {f} #/100cc").format(
                *raw[6:]
            )
        elif fmt.endswith("cf"):
            secs = time.strftime("%F %T:", time.localtime(secs))
            f = "{:" + (fmt[:-2] or ".0") + "%}"
            raw = f"CF1 {f}, CF2.5 {f}, CF10 {f}".format(
                raw[3] / raw[0], raw[4] / raw[1], raw[5] / raw[2]
            )
    elif sensor is SDS01x:
        obs = sensor(secs, *raw[-2:])
        raw = tuple(r / 10 for r in raw[-2:])
        if fmt.endswith("csv"):
            secs = f"{secs},"
            f = "{:" + (fmt[:-3] or ".1") + "f}"
            raw = ", ".join(map(f.format, raw))
        elif fmt.endswith("pm"):
            secs = time.strftime("%F %T:", time.localtime(secs))
            f = "{:" + (fmt[:-2] or "0.1") + "f}"
            raw = f"PM2.5 {f}, PM10 {f} ug/m3".format(*raw)
    else:
        raise ValueError(f"Unknown sensor {sensor.name}")

    assert f"{obs:{fmt}}" == f"{secs} {raw}"
