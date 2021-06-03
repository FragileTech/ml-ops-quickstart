from omegaconf import DictConfig
import pytest

from mloq.writer import CMDRecord
from mloq.command import GlobalsCMD
from mloq.test.commands.test_command import example_files, TestCommand


globals_conf = DictConfig(
    {
        "globals": {
            "project_name": "test name",
            "default_branch": "test_branch",
            "owner": "test_owner",
            "author": "test_author",
            "email": "test_email",
            "description": "test_description",
            "open_source": True,
            "project_url": "???",
        }
    }
)


@pytest.fixture(params=[(GlobalsCMD, globals_conf)], scope="function")
def command_and_config(request):
    command_cls, conf_dict = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, config


class TestGlobalsCMD:
    def test_default_project_url(self, command_and_config):
        command, config = command_and_config
        record = command.run()
        example = "https://github.com/test_owner/test-name"
        assert record.config.globals.project_url == example

    def test_non_default_project_url(self):
        example = "https://my_custom_url"
        non_empty_url = DictConfig(
            {
                "globals": {
                    "project_name": "test name",
                    "default_branch": "test_branch",
                    "owner": "test_owner",
                    "author": "test_author",
                    "email": "test_email",
                    "description": "test_description",
                    "open_source": True,
                    "project_url": example,
                }
            }
        )
        cmd = GlobalsCMD(record=CMDRecord(non_empty_url))
        record = cmd.run()
        assert record.config.globals.project_url == example
