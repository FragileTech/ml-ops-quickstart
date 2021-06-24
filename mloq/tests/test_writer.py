from tempfile import TemporaryDirectory

import pytest

from mloq.record import CMDRecord
from mloq.tests.test_record import config_examples
from mloq.writer import Writer


@pytest.fixture(params=config_examples, scope="function")
def writer(request):
    temp_dir = TemporaryDirectory()
    record = CMDRecord(request.param)
    yield Writer(record=record, path=temp_dir.name)
    temp_dir.cleanup()


class TestWriter:
    def test_init(self, writer):
        pass
