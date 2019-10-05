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
    from pms.pm.obsdata import PMSx003, SDS01x, HPMA115S0, HPMA115C0, SPS30
    from pms import SensorWarning
except ModuleNotFoundError as e:
    print(__doc__)
    raise


@pytest.mark.parametrize("fmt", "csv 4csv 04csv pm 4pm 04pm num 4num 04num cf .2cf 4.2cf".split())
def test_PMSx003_format(fmt, raw=tuple(range(1, 13)), secs=1567198523, sensor=PMSx003):
    obs = sensor(secs, *raw)
    raw = raw[:6] + tuple(x / 100 for x in raw[6:])
    if fmt.endswith("csv"):
        secs = f"{secs},"
        d = fmt[:-3] + "d"
        f = fmt[:-3] + ".2f"
        raw = ", ".join([*map(f"{{:{d}}}".format, raw[:6]), *map(f"{{:{f}}}".format, raw[6:])])
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        f = fmt[:-2] + "d"
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f=f, *raw[3:6])
    elif fmt.endswith("num"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        f = (fmt[:-3] or ".2") + "f"
        raw = (
            "N0.3 {:{f}}, N0.5 {:{f}}, N1.0 {:{f}}, N2.5 {:{f}}, N5.0 {:{f}}, N10 {:{f}} #/cm3"
        ).format(f=f, *raw[6:])
    elif fmt.endswith("cf"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        f = (fmt[:-2] or ".0") + "%"
        raw = "CF1 {:{f}}, CF2.5 {:{f}}, CF10 {:{f}}".format(
            raw[3] / raw[0], raw[4] / raw[1], raw[5] / raw[2], f=f
        )
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv .2csv 4.2csv pm .2pm 4.2pm".split())
def test_SDS01x_format(fmt, raw=(11, 12), secs=1567198523, sensor=SDS01x):

    obs = sensor(secs, *raw)
    raw = tuple(r / 10 for r in raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        f = (fmt[:-3] or ".1") + "f"
        raw = ", ".join(map(f"{{:{f}}}".format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        f = (fmt[:-2] or "0.1") + "f"
        raw = "PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f=f, *raw)
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv 4csv 04csv pm 4pm 04pm".split())
def test_HPMA115S0_format(fmt, raw=(11, 12), secs=1567198523, sensor=HPMA115S0):
    obs = sensor(secs, *raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        f = fmt[:-3] + "d"
        raw = ", ".join(map(f"{{:{f}}}".format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        f = fmt[:-2] + "d"
        raw = "PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f=f, *raw)
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv 4csv 04csv pm 4pm 04pm".split())
def test_HPMA115C0_format(fmt, raw=(11, 12, 13, 14), secs=1567198523, sensor=HPMA115C0):
    obs = sensor(secs, *raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        f = fmt[:-3] + "d"
        raw = ", ".join(map(f"{{:{f}}}".format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        f = fmt[:-2] + "d"
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM4 {:{f}}, PM10 {:{f}} ug/m3".format(f=f, *raw)
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv .2csv 4.2csv pm .2pm 4.2pm".split())
def test_SPS30_format(fmt, raw=range(100, 110), secs=1567198523, sensor=SPS30):

    obs = sensor(secs, *raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        f = (fmt[:-3] or ".2") + "f"
        raw = ", ".join(map(f"{{:{f}}}".format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        f = (fmt[:-2] or ".2") + "f"
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM4 {:{f}}, PM10 {:{f}} ug/m3".format(f=f, *raw)
    assert f"{obs:{fmt}}" == f"{secs} {raw}"
