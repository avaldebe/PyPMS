import pytest

from pms.core.reader import MessageReader
from pms.core.sensor import Sensor
from tests.conftest import CAPTURED_DATA


@pytest.fixture
def reader() -> MessageReader:
    return MessageReader(CAPTURED_DATA, Sensor["PMS3003"])


def test_reader(reader: MessageReader):
    with reader:
        values = tuple(reader())

    assert len(values) == 10


def test_closed(reader: MessageReader):
    values = tuple(reader())
    assert len(values) == 0
