from pathlib import Path

from omegaconf import DictConfig
import pytest

from mloq.commands.package import setup_py
from mloq.files import File, mloq_yml
from mloq.record import CMDRecord, Ledger
from tests.commands.test_docs import docs_conf, docs_conf_with_globals


@pytest.fixture(scope="function")
def ledger():
    return Ledger()


_files = [mloq_yml, setup_py]


@pytest.fixture(params=_files, scope="class")
def file(request):
    return request.param


@pytest.fixture(scope="class")
def files():
    return _files


config_examples = [None, DictConfig({}), DictConfig(docs_conf), DictConfig(docs_conf_with_globals)]
config_ids = ["config-is-None", "empty-dict", "docs-conf", "docs-conf-with-globals"]


@pytest.fixture(params=config_examples, scope="function", ids=config_ids)
def record(request):
    return CMDRecord(request.param)


@pytest.fixture(scope="class")
def directories():
    return [Path(), Path("test directory"), "test_str_directory"]


@pytest.fixture(params=config_examples[1:], scope="class")
def config(request):
    return request.param


class TestLedger:
    def test_files(self, ledger, files):
        for file in files:
            ledger.register(file)
        assert isinstance(ledger.files, list)
        assert len(ledger.files) == len(files)
        for item in ledger.files:
            assert isinstance(item, tuple)
            assert isinstance(item[0], str)
            assert isinstance(item[1], str)

    def test_register_no_description(self, ledger, file):
        ledger.register(file)
        assert (str(Path(file.dst)), file.description) in ledger.files
        assert (Path(file.dst), file.description) == ledger._files[0]

    def test_register_description_str(self, ledger):
        file, description = f"example/{mloq_yml.dst}", "test_description"
        ledger.register(file, description=description)
        assert (str(Path(file)), description) in ledger.files
        assert (Path(file), description) == ledger._files[0]

    def test_register_description_file(self, ledger, file):
        description = f"example/{mloq_yml.dst}", "test_description"
        ledger.register(file, description=description)
        assert (str(Path(file.dst)), description) in ledger.files
        assert (Path(file.dst), description) == ledger._files[0]

    def test_no_description_fails(self, ledger):
        with pytest.raises(ValueError):
            ledger.register("error_file.txt")


class TestCMDRecord:
    def test_attribute_types(self, record, files, directories):
        assert isinstance(record.config, DictConfig)
        assert isinstance(record.files, dict)
        for file in files:
            record.register_file(file, Path())
        for k, v in record.files.items():
            assert isinstance(k, Path)
            assert isinstance(v, File)
        for directory in directories:
            record.register_directory(directory)
        assert isinstance(record.directories, list)
        for directory in record.directories:
            assert isinstance(directory, Path)

    def test_register_file_no_description(self, record, files):
        example_path = Path("miau")
        for file in files:
            record.register_file(file, example_path)
        for file, (k, v) in zip(files, record.files.items()):
            assert example_path / file.dst == k
            assert file == v

    def test_register_file_with_description(self, record, files):
        example_path = Path("miau")
        example_description = "This is an example description"
        for file in files:
            record.register_file(file, example_path, description=example_description)
        for file, (k, v) in zip(files, record.files.items()):
            assert example_path / file.dst == k
            example_file = File(
                name=file.name,
                src=file.src,
                dst=file.dst,
                description=example_description,
                is_static=file.is_static,
            )
            assert example_file == v

    def test_register_fails_no_description(self, record, file):
        example_file = File(
            name=file.name,
            src=file.src,
            dst=file.dst,
            description="",
            is_static=file.is_static,
        )
        with pytest.raises(ValueError):
            record.register_file(example_file, path=Path())

    def test_register_directory(self, record, directories):
        for directory in directories:
            record.register_directory(directory)
        for directory, _ in zip(record.directories, directories):
            assert directory == Path(directory)

    def test_update_config(self, record, config):
        record.update_config(config)
        # TODO: Find a nice way to test this
        # assert record.config == config
