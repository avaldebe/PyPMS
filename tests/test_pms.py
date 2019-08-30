import sys
from pathlib import Path
import time
import pytest

# There must ba a better way
PROJECTPATH = Path(__file__).parents[1]
sys.path.append(str(PROJECTPATH))
import pms


def test_format():
    sec, raw = 1567198523, tuple(range(9))
    obs = pms.Obs(sec, *raw)

    _time = time.strftime("%F %T", time.localtime(sec))
    assert obs.timestamp() == _time, "format: timestamp"

    for fmt in ["", "4", "04"]:
        _fmt = "{:" + fmt + "d}"

        _obs = f"{obs:{fmt}csv}"
        _raw = ", ".join(map(_fmt.format, raw))
        assert _obs == f"{sec}, {_raw}", f"format: '{fmt}csv'"

        _obs = f"{obs:{fmt}pm}"
        _raw = f"PM1 {_fmt}, PM2.5 {_fmt}, PM10 {_fmt} ug/m3".format(*raw[:4])
        assert _obs == f"{_time}: {_raw}", f"format: '{fmt}pm'"

        _obs = f"{obs:{fmt}num}"
        _raw = (
            f"N0.3 {_fmt}, N0.5 {_fmt}, N1.0 {_fmt}, "
            f"N2.5 {_fmt}, N5.0 {_fmt}, N10 {_fmt} #/100cc"
        ).format(*raw[3:])
        assert _obs == f"{_time}: {_raw}", f"format: '{fmt}num'"
