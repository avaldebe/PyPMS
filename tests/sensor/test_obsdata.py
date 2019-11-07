import os, time
import pytest

os.environ["LEVEL"] = "DEBUG"
from pms.sensor import pm
from pms import SensorWarning


@pytest.mark.parametrize("fmt", "csv pm num cf raw".split())
def test_PMSx003_format(fmt, raw=tuple(range(1, 13)), secs=1567198523, sensor=pm.PMSx003):
    obs = sensor.ObsData(secs, *raw)
    raw = raw[:6] + tuple(x / 100 for x in raw[6:])
    if fmt.endswith("csv"):
        secs = f"{secs},"
        raw = ", ".join(["{:d}"] * 3 + ["{:.1f}"] * 3 + ["{:.2f}"] * 6).format(*raw)
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f=".1f", *raw[3:6])
    elif fmt.endswith("num"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = (
            "N0.3 {:{f}}, N0.5 {:{f}}, N1.0 {:{f}}, N2.5 {:{f}}, N5.0 {:{f}}, N10 {:{f}} #/cm3"
        ).format(f=".2f", *raw[6:])
    elif fmt.endswith("cf"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "CF1 {:{f}}, CF2.5 {:{f}}, CF10 {:{f}}".format(
            raw[3] / raw[0], raw[4] / raw[1], raw[5] / raw[2], f=".0%"
        )
    elif fmt.endswith("raw"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f="d", *raw[:3])
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv pm num cf raw hcho atm".split())
def test_PMS5003ST_format(fmt, raw=tuple(range(1, 16)), secs=1567198523, sensor=pm.PMS5003ST):
    obs = sensor.ObsData(secs, *raw)
    raw = raw[:6] + tuple(x / 100 for x in raw[6:12]) + (raw[12],) + tuple(x / 10 for x in raw[13:])
    if fmt.endswith("csv"):
        secs = f"{secs},"
        raw = ", ".join(
            ["{:d}"] * 3 + ["{:.1f}"] * 3 + ["{:.2f}"] * 6 + ["{:d}"] + ["{:.1f}"] * 2
        ).format(*raw)
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f=".1f", *raw[3:6])
    elif fmt.endswith("num"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = (
            "N0.3 {:{f}}, N0.5 {:{f}}, N1.0 {:{f}}, N2.5 {:{f}}, N5.0 {:{f}}, N10 {:{f}} #/cm3"
        ).format(f=".2f", *raw[6:])
    elif fmt.endswith("cf"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "CF1 {:{f}}, CF2.5 {:{f}}, CF10 {:{f}}".format(
            raw[3] / raw[0], raw[4] / raw[1], raw[5] / raw[2], f=".0%"
        )
    elif fmt.endswith("raw"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f="d", *raw[:3])
    elif fmt.endswith("hcho"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = f"HCHO {raw[-3]} ug/m3"
    elif fmt.endswith("atm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = f"Temp. {raw[-2]:.1f} °C, Rel.Hum. {raw[-1]:.1f} %"
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv pm num cf raw atm".split())
def test_PMS5003T_format(fmt, raw=tuple(range(1, 13)), secs=1567198523, sensor=pm.PMS5003T):
    obs = sensor.ObsData(secs, *raw)
    raw = raw[:6] + tuple(x / 100 for x in raw[6:-2]) + tuple(x / 10 for x in raw[-2:])
    if fmt.endswith("csv"):
        secs = f"{secs},"
        raw = ", ".join(["{:d}"] * 3 + ["{:.1f}"] * 3 + ["{:.2f}"] * 4 + ["{:.1f}"] * 2).format(
            *raw
        )
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f=".1f", *raw[3:6])
    elif fmt.endswith("num"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = ("N0.3 {:{f}}, N0.5 {:{f}}, N1.0 {:{f}}, N2.5 {:{f}} #/cm3").format(
            f=".2f", *raw[6:-2]
        )
    elif fmt.endswith("cf"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "CF1 {:{f}}, CF2.5 {:{f}}, CF10 {:{f}}".format(
            raw[3] / raw[0], raw[4] / raw[1], raw[5] / raw[2], f=".0%"
        )
    elif fmt.endswith("raw"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f="d", *raw[:3])
    elif fmt.endswith("atm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = f"Temp. {raw[-2]:.1f} °C, Rel.Hum. {raw[-1]:.1f} %"
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv pm".split())
def test_SDS01x_format(fmt, raw=(11, 12), secs=1567198523, sensor=pm.SDS01x):

    obs = sensor.ObsData(secs, *raw)
    raw = tuple(r / 10 for r in raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        raw = ", ".join(map("{:.1f}".format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f=".1f", *raw)
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv pm".split())
def test_SDS198_format(fmt, raw=123, secs=1567198523, sensor=pm.SDS198):

    obs = sensor.ObsData(secs, raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        raw = f"{raw:.1f}"
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = f"PM100 {raw:.1f} ug/m3"
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv pm".split())
def test_HPMA115S0_format(fmt, raw=(11, 12), secs=1567198523, sensor=pm.HPMA115S0):
    obs = sensor.ObsData(secs, *raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        raw = ", ".join(map("{:.1f}".format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM2.5 {:{f}}, PM10 {:{f}} ug/m3".format(f=".1f", *raw)
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv pm".split())
def test_HPMA115C0_format(fmt, raw=(11, 12, 13, 14), secs=1567198523, sensor=pm.HPMA115C0):
    obs = sensor.ObsData(secs, *raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        raw = ", ".join(map("{:.1f}".format, raw))
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM4 {:{f}}, PM10 {:{f}} ug/m3".format(f=".1f", *raw)
    assert f"{obs:{fmt}}" == f"{secs} {raw}"


@pytest.mark.parametrize("fmt", "csv pm num diam".split())
def test_SPS30_format(fmt, raw=range(100, 110), secs=1567198523, sensor=pm.SPS30):

    obs = sensor.ObsData(secs, *raw)
    if fmt.endswith("csv"):
        secs = f"{secs},"
        raw = ", ".join(["{:.1f}"] * 4 + ["{:.2f}"] * 5 + ["{:.1f}"]).format(*raw)
    elif fmt.endswith("pm"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "PM1 {:{f}}, PM2.5 {:{f}}, PM4 {:{f}}, PM10 {:{f}} ug/m3".format(f=".1f", *raw[:4])
    elif fmt.endswith("num"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "N0.5 {:{f}}, N1.0 {:{f}}, N2.5 {:{f}}, N4.0 {:{f}}, N10 {:{f}} #/cm3".format(
            f=".2f", *raw[4:-1]
        )
    elif fmt.endswith("diam"):
        secs = time.strftime("%F %T:", time.localtime(secs))
        raw = "Ø {:{f}} μm".format(raw[-1], f=".1f")
    assert f"{obs:{fmt}}" == f"{secs} {raw}"
