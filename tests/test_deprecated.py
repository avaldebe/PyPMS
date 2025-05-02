import pytest
from packaging.version import Version

from pms import __version__

from .sensors.test_sensor import GoodData

pytestmark = pytest.mark.skipif(
    Version(__version__) >= Version("1.0"),
    reason="deprecated module should be removed on 1.0 release",
)


def test_deprecated_module():
    with pytest.deprecated_call():
        import pms.sensor  # noqa: F401


@pytest.mark.parametrize("obs", GoodData.test_obs())
def test_deprecated_method(obs):
    with pytest.deprecated_call():
        obs.subset()
