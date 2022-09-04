from pathlib import Path

from omegaconf import DictConfig, OmegaConf
import pytest

from mloq.commands.setup import SetupCMD
from mloq.files import mloq_yml
from mloq.writer import CMDRecord
from tests.test_command import command_and_example, TestCommand


@pytest.fixture(scope="function")
def command_and_config():
    config = OmegaConf.load(Path(__file__).parent.parent / "examples" / mloq_yml.dst)
    record = CMDRecord(config)
    command = SetupCMD(record=record)
    return command, config


class __TestSetupCMD:
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
        setup_command, config = command_and_config
        setup_command.parse_config()
        for command in setup_command.sub_commands:
            for key in command.config.keys():
                conf_record = getattr(setup_command.record.config, command.cmd_name)
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
        setup_command, config = command_and_config
        setup_command.record_directories()
        for command in setup_command.sub_commands:
            for directory in command.directories:
                assert directory in setup_command.record.directories
            for directory in setup_command.record.directories:
                assert directory in command.directories

    def __test_run(self, command_and_config):
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

    def __test_files_have_correct_path(self, command_and_example):
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
