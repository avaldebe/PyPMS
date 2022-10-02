import sys

if sys.version_info >= (3, 10):  # pragma: no cover
    from importlib import metadata
else:  # pragma: no cover
    import importlib_metadata as metadata

import pytest
from packaging.version import Version

from .sensors.test_sensor import GoodData

version = Version(metadata.version("PyPMS"))
pytestmark = pytest.mark.skipif(
    version >= Version("1.0"), reason="deprecated module should be removed on 1.0 release"
)


def test_deprecated_module():
    with pytest.deprecated_call():
        import pms.sensor


@pytest.mark.parametrize("obs", GoodData.test_obs())
def test_deprecated_method(obs):
    with pytest.deprecated_call():
        obs.subset()
