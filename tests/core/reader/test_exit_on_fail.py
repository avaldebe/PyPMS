import pytest

from pms.core.reader import Reader, UnableToRead, exit_on_fail


class MockReader(Reader):
    def __init__(self, raise_on_enter=False):
        self.raise_on_enter = raise_on_enter

    def __call__(self):
        raise NotImplementedError()

    def open(self):
        if self.raise_on_enter:
            raise UnableToRead()
        self.entered = True

    def close(self):
        self.exited = True


@pytest.fixture()
def reader(monkeypatch) -> MockReader:
    # prevent the helper exiting the test suite
    monkeypatch.setattr("pms.core.reader.sys.exit", lambda: None)
    return MockReader()


@pytest.fixture()
def reader_error(monkeypatch) -> MockReader:
    def sys_exit(*args):
        raise Exception("exit")

    # prevent the helper exiting the test suite
    monkeypatch.setattr("pms.core.reader.sys.exit", sys_exit)
    return MockReader(raise_on_enter=True)


def test_reader(reader: MockReader):
    with exit_on_fail(reader) as yielded:
        assert yielded == reader

    assert reader.entered
    assert reader.exited


def test_reader_error(reader_error: MockReader):
    with pytest.raises(Exception) as e:
        with exit_on_fail(reader_error):
            raise Exception("should not get here")

    assert "exit" in str(e.value)  # type:ignore[unreachable,unused-ignore]
