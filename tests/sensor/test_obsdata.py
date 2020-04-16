import os, time
from dataclasses import asdict
import pytest

os.environ["LEVEL"] = "DEBUG"
from pms.sensor import pm
from pms import SensorWarning


@pytest.mark.parametrize("fmt", "header csv pm num cf raw error".split())
def test_PMSx003_format(fmt, raw=tuple(range(1, 13)), secs=1_567_198_523, sensor=pm.PMSx003):
    obs = sensor.ObsData(secs, *raw)
    raw = raw[:6] + tuple(x / 100 for x in raw[6:])
    obs_fmt = dict(
        header=", ".join(asdict(obs).keys()),
        csv="{}, {:d}, {:d}, {:d}, {:.1f}, {:.1f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(
            secs, *raw
        ),
        pm="{}: PM1 {:.1f}, PM2.5 {:.1f}, PM10 {:.1f} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[3:6]
        ),
        num="{}: N0.3 {:.2f}, N0.5 {:.2f}, N1.0 {:.2f}, N2.5 {:.2f}, N5.0 {:.2f}, N10 {:.2f} #/cm3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[6:]
        ),
        cf="{}: CF1 {:.0%}, CF2.5 {:.0%}, CF10 {:.0%}".format(
            time.strftime("%F %T", time.localtime(secs)),
            raw[3] / raw[0],
            raw[4] / raw[1],
            raw[5] / raw[2],
        ),
        raw="{}: PM1 {:d}, PM2.5 {:d}, PM10 {:d} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[:3]
        ),
    )

    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt]
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm num cf raw hcho atm error".split())
def test_PMS5003ST_format(fmt, raw=tuple(range(1, 16)), secs=1_567_198_523, sensor=pm.PMS5003ST):
    obs = sensor.ObsData(secs, *raw)
    raw = raw[:6] + tuple(x / 100 for x in raw[6:12]) + (raw[12],) + tuple(x / 10 for x in raw[13:])
    obs_fmt = dict(
        header=", ".join(asdict(obs).keys()),
        csv="{}, {:d}, {:d}, {:d}, {:.1f}, {:.1f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}, {:.1f}, {:.1f}".format(
            secs, *raw
        ),
        pm="{}: PM1 {:.1f}, PM2.5 {:.1f}, PM10 {:.1f} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[3:6]
        ),
        num="{}: N0.3 {:.2f}, N0.5 {:.2f}, N1.0 {:.2f}, N2.5 {:.2f}, N5.0 {:.2f}, N10 {:.2f} #/cm3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[6:-3]
        ),
        cf="{}: CF1 {:.0%}, CF2.5 {:.0%}, CF10 {:.0%}".format(
            time.strftime("%F %T", time.localtime(secs)),
            raw[3] / raw[0],
            raw[4] / raw[1],
            raw[5] / raw[2],
        ),
        raw="{}: PM1 {:d}, PM2.5 {:d}, PM10 {:d} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[:3]
        ),
        hcho="{}: HCHO {} mg/m3".format(time.strftime("%F %T", time.localtime(secs)), raw[-3]),
        atm="{}: Temp. {:.1f} °C, Rel.Hum. {:.1f} %".format(
            time.strftime("%F %T", time.localtime(secs)), raw[-2], raw[-1]
        ),
    )

    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt]
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm num cf raw atm error".split())
def test_PMS5003T_format(fmt, raw=tuple(range(1, 13)), secs=1_567_198_523, sensor=pm.PMS5003T):
    obs = sensor.ObsData(secs, *raw)
    raw = raw[:6] + tuple(x / 100 for x in raw[6:-2]) + tuple(x / 10 for x in raw[-2:])
    obs_fmt = dict(
        header=", ".join(asdict(obs).keys()),
        csv="{}, {:d}, {:d}, {:d}, {:.1f}, {:.1f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.1f}, {:.1f}".format(
            secs, *raw
        ),
        pm="{}: PM1 {:.1f}, PM2.5 {:.1f}, PM10 {:.1f} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[3:6]
        ),
        num="{}: N0.3 {:.2f}, N0.5 {:.2f}, N1.0 {:.2f}, N2.5 {:.2f} #/cm3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[6:-2]
        ),
        cf="{}: CF1 {:.0%}, CF2.5 {:.0%}, CF10 {:.0%}".format(
            time.strftime("%F %T", time.localtime(secs)),
            raw[3] / raw[0],
            raw[4] / raw[1],
            raw[5] / raw[2],
        ),
        raw="{}: PM1 {:d}, PM2.5 {:d}, PM10 {:d} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[:3]
        ),
        atm="{}: Temp. {:.1f} °C, Rel.Hum. {:.1f} %".format(
            time.strftime("%F %T", time.localtime(secs)), raw[-2], raw[-1]
        ),
    )

    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt]
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_SDS01x_format(fmt, raw=(11, 12), secs=1_567_198_523, sensor=pm.SDS01x):

    obs = sensor.ObsData(secs, *raw)
    raw = tuple(r / 10 for r in raw)
    obs_fmt = dict(
        header=", ".join(asdict(obs).keys()),
        csv=f"{secs}, " + ", ".join(map("{:.1f}".format, raw)),
        pm="{}: PM2.5 {:.1f}, PM10 {:.1f} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw
        ),
    )

    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt]
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_SDS198_format(fmt, raw=123, secs=1_567_198_523, sensor=pm.SDS198):

    obs = sensor.ObsData(secs, raw)
    obs_fmt = dict(
        header=", ".join(asdict(obs).keys()),
        csv=f"{secs}, {raw:.1f}",
        pm="{}: PM100 {:.1f} ug/m3".format(time.strftime("%F %T", time.localtime(secs)), raw),
    )

    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt]
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_HPMA115S0_format(fmt, raw=(11, 12), secs=1_567_198_523, sensor=pm.HPMA115S0):
    obs = sensor.ObsData(secs, *raw)
    obs_fmt = dict(
        header=", ".join(asdict(obs).keys()),
        csv=f"{secs}, " + ", ".join(map("{:.1f}".format, raw)),
        pm="{}: PM2.5 {:.1f}, PM10 {:.1f} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw
        ),
    )

    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt]
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_HPMA115C0_format(fmt, raw=(11, 12, 13, 14), secs=1_567_198_523, sensor=pm.HPMA115C0):
    obs = sensor.ObsData(secs, *raw)
    obs_fmt = dict(
        header=", ".join(asdict(obs).keys()),
        csv=f"{secs}, " + ", ".join(map("{:.1f}".format, raw)),
        pm="{}: PM1 {:.1f}, PM2.5 {:.1f}, PM4 {:.1f}, PM10 {:.1f} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw
        ),
    )

    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt]
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm num diam error".split())
def test_SPS30_format(fmt, raw=range(100, 110), secs=1_567_198_523, sensor=pm.SPS30):

    obs = sensor.ObsData(secs, *raw)
    obs_fmt = dict(
        header=", ".join(asdict(obs).keys()),
        csv="{}, {:.1f}, {:.1f}, {:.1f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.1f}".format(
            secs, *raw
        ),
        pm="{}: PM1 {:.1f}, PM2.5 {:.1f}, PM4 {:.1f}, PM10 {:.1f} ug/m3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[:4]
        ),
        num="{}: N0.5 {:.2f}, N1.0 {:.2f}, N2.5 {:.2f}, N4.0 {:.2f}, N10 {:.2f} #/cm3".format(
            time.strftime("%F %T", time.localtime(secs)), *raw[4:-1]
        ),
        diam="{}: Ø {:.1f} μm".format(time.strftime("%F %T", time.localtime(secs)), raw[-1]),
    )

    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt]
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")
