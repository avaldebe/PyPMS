from importlib import metadata

from pms import __version__


def test_version():
    assert 3 <= len(__version__.split(".")) <= 5
    assert metadata.version("PyPMS") == __version__
