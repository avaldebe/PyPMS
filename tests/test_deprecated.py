import sys

if sys.version_info >= (3, 10):  # pragma: no cover
    from importlib import metadata
else:  # pragma: no cover
    import importlib_metadata as metadata

import pytest

from .sensor.test_sensor import GoodData

sem_ver: str = metadata.version("PyPMS")
version = tuple(int(v) for v in sem_ver.split("."))


@pytest.mark.skipif(version >= (1, 0), reason="deprecated module should be removed on 1.0 release")
def test_deprecated_module():
    with pytest.deprecated_call():
        import pms.sensor


@pytest.mark.skipif(version >= (1, 0), reason="deprecated module should be removed on 1.0 release")
@pytest.mark.parametrize("obs", GoodData.test_obs())
def test_deprecated_method(obs):
    with pytest.deprecated_call():
        obs.subset()
