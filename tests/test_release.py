import sys
from os import getenv
from subprocess import check_output

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from pytest import mark


@mark.xfail(reason="only relevant for new tags and releases")
def test_package_version():
    version = metadata.version("PyPMS")
    git_tag = check_output("git describe".split())
    assert version == git_tag
