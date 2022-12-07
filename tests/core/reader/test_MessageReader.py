import pytest

from pms.core.reader import MessageReader
from pms.core.sensor import Sensor
from tests.conftest import captured_data


@pytest.fixture
def reader() -> MessageReader:
    return MessageReader(captured_data, Sensor["PMS3003"])


def test_reader(reader: MessageReader):
    with reader:
        values = tuple(reader())

    assert len(values) == 10


def test_closed(reader: MessageReader):
    values = tuple(reader())
    assert len(values) == 0
