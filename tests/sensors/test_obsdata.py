import time
from dataclasses import asdict

import pytest

from pms.sensors.bosch_sensortec import mcu680
from pms.sensors.honeywell import hpma115c0, hpma115s0
from pms.sensors.novafitness import sds01x, sds198
from pms.sensors.plantower import pms5003st, pms5003t, pmsx003
from pms.sensors.sensirion import sps30
from pms.sensors.winsen import mhz19b, zh0xx


@pytest.mark.parametrize("fmt", "header csv pm num cf raw error".split())
def test_PMSx003_format(fmt, data=tuple(range(1, 13)), secs=1_567_198_523, sensor=pmsx003):
    obs = sensor.ObsData(secs, *data)
    data = data[:6] + tuple(x / 100 for x in data[6:])
    obs_fmt = dict(
        raw="{0}: PM1 {1:d}, PM2.5 {2:d}, PM10 {3:d} μg/m3",
        pm="{0}: PM1 {4:.1f}, PM2.5 {5:.1f}, PM10 {6:.1f} μg/m3",
        num="{0}: N0.3 {7:.2f}, N0.5 {8:.2f}, N1.0 {9:.2f}, N2.5 {10:.2f}, N5.0 {11:.2f}, N10 {12:.2f} #/cm3",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:d}, {:d}, {:d}, {:.1f}, {:.1f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    elif fmt == "cf":
        cf = "{}: CF1 {:.0%}, CF2.5 {:.0%}, CF10 {:.0%}"
        assert f"{obs:{fmt}}" == cf.format(
            date, data[3] / data[0], data[4] / data[1], data[5] / data[2]
        )
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm num cf raw hcho atm error".split())
def test_PMS5003ST_format(fmt, data=list(range(1, 16)), secs=1_567_198_523, sensor=pms5003st):
    obs = sensor.ObsData(secs, *data)
    data[6:12] = [x / 100 for x in data[6:12]]
    data[12] /= 1000
    data[13] /= 10
    data[14] /= 10
    obs_fmt = dict(
        raw="{0}: PM1 {1:d}, PM2.5 {2:d}, PM10 {3:d} μg/m3",
        pm="{0}: PM1 {4:.1f}, PM2.5 {5:.1f}, PM10 {6:.1f} μg/m3",
        num="{0}: N0.3 {7:.2f}, N0.5 {8:.2f}, N1.0 {9:.2f}, N2.5 {10:.2f}, N5.0 {11:.2f}, N10 {12:.2f} #/cm3",
        hcho="{0}: HCHO {13:.3f} mg/m3",
        atm="{0}: Temp. {14:.1f} °C, Rel.Hum. {15:.1f} %",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:d}, {:d}, {:d}, {:.1f}, {:.1f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.3f}, {:.1f}, {:.1f}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    elif fmt == "cf":
        cf = "{}: CF1 {:.0%}, CF2.5 {:.0%}, CF10 {:.0%}"
        assert f"{obs:{fmt}}" == cf.format(
            date, data[3] / data[0], data[4] / data[1], data[5] / data[2]
        )
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm num cf raw atm error".split())
def test_PMS5003T_format(fmt, data=tuple(range(1, 13)), secs=1_567_198_523, sensor=pms5003t):
    obs = sensor.ObsData(secs, *data)
    data = data[:6] + tuple(x / 100 for x in data[6:-2]) + tuple(x / 10 for x in data[-2:])
    obs_fmt = dict(
        raw="{0}: PM1 {1:d}, PM2.5 {2:d}, PM10 {3:d} μg/m3",
        pm="{0}: PM1 {4:.1f}, PM2.5 {5:.1f}, PM10 {6:.1f} μg/m3",
        num="{0}: N0.3 {7:.2f}, N0.5 {8:.2f}, N1.0 {9:.2f}, N2.5 {10:.2f} #/cm3",
        atm="{0}: Temp. {11:.1f} °C, Rel.Hum. {12:.1f} %",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:d}, {:d}, {:d}, {:.1f}, {:.1f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.1f}, {:.1f}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    elif fmt == "cf":
        cf = "{}: CF1 {:.0%}, CF2.5 {:.0%}, CF10 {:.0%}"
        assert f"{obs:{fmt}}" == cf.format(
            date, data[3] / data[0], data[4] / data[1], data[5] / data[2]
        )
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_SDS01x_format(fmt, data=(11, 12), secs=1_567_198_523, sensor=sds01x):
    obs = sensor.ObsData(secs, *data)
    data = tuple(r / 10 for r in data)
    obs_fmt = dict(
        pm="{}: PM2.5 {:.1f}, PM10 {:.1f} μg/m3",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:.1f}, {:.1f}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_SDS198_format(fmt, data=123, secs=1_567_198_523, sensor=sds198):
    obs = sensor.ObsData(secs, data)
    obs_fmt = dict(
        pm="{}: PM100 {:.1f} μg/m3",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:.1f}"
        assert f"{obs:{fmt}}" == csv.format(secs, data)
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_HPMA115S0_format(fmt, data=(11, 12), secs=1_567_198_523, sensor=hpma115s0):
    obs = sensor.ObsData(secs, *data)
    obs_fmt = dict(
        pm="{}: PM2.5 {:.1f}, PM10 {:.1f} μg/m3",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:.1f}, {:.1f}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_HPMA115C0_format(fmt, data=(11, 12, 13, 14), secs=1_567_198_523, sensor=hpma115c0):
    obs = sensor.ObsData(secs, *data)
    obs_fmt = dict(
        pm="{}: PM1 {:.1f}, PM2.5 {:.1f}, PM4 {:.1f}, PM10 {:.1f} μg/m3",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:.1f}, {:.1f}, {:.1f}, {:.1f}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm num diam error".split())
def test_SPS30_format(fmt, data=range(100, 110), secs=1_567_198_523, sensor=sps30):
    obs = sensor.ObsData(secs, *data)
    obs_fmt = dict(
        pm="{0}: PM1 {1:.1f}, PM2.5 {2:.1f}, PM4 {3:.1f}, PM10 {4:.1f} μg/m3",
        num="{0}: N0.5 {5:.2f}, N1.0 {6:.2f}, N2.5 {7:.2f}, N4.0 {8:.2f}, N10 {9:.2f} #/cm3",
        diam="{0}: Ø {10:.1f} μm",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:.1f}, {:.1f}, {:.1f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.1f}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv atm bme bsec error".split())
def test_mcu680_format(fmt, data=list(range(100, 107)), secs=1_567_198_523, sensor=mcu680):
    obs = sensor.ObsData(secs, *data)
    data[0] /= 100
    data[1] /= 100
    data[2] = (int(data[2]) << 8 | data[3]) / 100
    data[3] = data[4] >> 4
    data[4] &= 0x0FFF
    data[5] /= 1000
    obs_fmt = dict(
        atm="{0}: Temp. {1:.1f} °C, Rel.Hum. {2:.1f} %, Press {3:.2f} hPa",
        bsec="{0}: Temp. {1:.1f} °C, Rel.Hum. {2:.1f} %, Press {3:.2f} hPa, {5} IAQ",
        bme="{0}: Temp. {1:.1f} °C, Rel.Hum. {2:.1f} %, Press {3:.2f} hPa, {6:.1f} kΩ",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {:.1f}, {:.1f}, {:.2f}, {:}, {:}, {:.1f}, {:}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header co2 csv error".split())
def test_mhz19b_format(fmt, data=(500,), secs=1_567_198_523, sensor=mhz19b):
    obs = sensor.ObsData(secs, *data)
    obs_fmt = dict(
        co2="{0}: CO2 {1} ppm",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{}, {}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")


@pytest.mark.parametrize("fmt", "header csv pm error".split())
def test_ZH0xx_format(fmt, data=(133, 150, 101), secs=1_567_198_523, sensor=zh0xx):
    obs = sensor.ObsData(secs, *data)
    obs_fmt = dict(
        pm="{0}: PM1 {3:.1f}, PM2.5 {1:.1f}, PM10 {2:.1f} μg/m3",
    )
    date = time.strftime("%F %T", time.localtime(secs))
    if fmt in obs_fmt:
        assert f"{obs:{fmt}}" == obs_fmt[fmt].format(date, *data)
    elif fmt == "header":
        assert f"{obs:{fmt}}" == ", ".join(asdict(obs).keys())
    elif fmt == "csv":
        csv = "{0}, {3:.1f}, {1:.1f}, {2:.1f}"
        assert f"{obs:{fmt}}" == csv.format(secs, *data)
    else:
        with pytest.raises(ValueError) as e:
            f"{obs:{fmt}}"
        assert str(e.value).startswith(f"Unknown format code '{fmt}'")
