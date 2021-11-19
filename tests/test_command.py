from pathlib import Path

from omegaconf import DictConfig
import pytest

from mloq.command import Command
from mloq.writer import CMDRecord


conf = {}


def is_namedtuple_instance(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(type(n) == str for n in f)


@pytest.fixture(params=[(Command, conf)], scope="function")
def command_and_config(request):
    command_cls, conf_dict = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, config


@pytest.fixture(params=[(Command, conf, None)], scope="function")
def command_and_example(request):
    command_cls, conf_dict, example = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, example


class TestCommand:
    def test_class_attributes(self, command_and_config):
        command, config = command_and_config
        assert isinstance(command.cmd_name, str)
        assert isinstance(command.files, tuple)
        assert isinstance(command.config, DictConfig)
        assert isinstance(command.directories, tuple)
        if len(command.directories) > 0:
            for directory in command.directories:
                assert isinstance(directory, Path)

    def test_parse_config(self, command_and_config):
        command, config = command_and_config
        if command.__class__.__name__ == "SetupCMD":
            return
        command.parse_config()
        for key in command.config.keys():
            conf_record = getattr(command.record.config, command.cmd_name)
            assert conf_record[key] == config[command.cmd_name][key]

    def test_files_present_in_record(self, command_and_config):
        command, config = command_and_config
        command.record_files()

        file_names = [f.name for f in command.files]
        file_srcs = [f.src for f in command.files]
        file_dsts = [f.dst for f in command.files]
        for f in command.record.files.values():
            assert f.name in file_names
            assert f.src in file_srcs
            assert f.dst in file_dsts

    def test_record_directories(self, command_and_config):
        command, config = command_and_config
        command.record_directories()
        for directory in command.directories:
            assert directory in command.record.directories
        for directory in command.record.directories:
            assert directory in command.directories

    def test_run(self, command_and_config):
        command, config = command_and_config
        record = command.run()
        for directory in command.directories:
            assert directory in record.directories

        file_names = [f.name for f in command.files]
        file_srcs = [f.src for f in command.files]
        file_dsts = [f.dst for f in command.files]
        for f in record.files.values():
            assert f.name in file_names
            assert f.src in file_srcs
            assert f.dst in file_dsts

    def test_files_have_correct_path(self, command_and_example):
        if not command_and_example:
            return
        command, example_files = command_and_example
        if example_files is None:
            return
        record = command.run()
        for path, file in record.files.items():
            assert path in example_files
            assert example_files[path] == file

        for path, file in example_files.items():
            assert path in record.files
            assert record.files[path] == file
