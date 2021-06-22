from pathlib import Path

from omegaconf import DictConfig, OmegaConf
import pytest

from mloq.commands.setup import SetupCMD
from mloq.files import conf_py, docs_req, index_md, make_bat_docs, makefile_docs
from mloq.test.test_command import example_files, TestCommand
from mloq.writer import CMDRecord


@pytest.fixture(scope="function")
def command_and_config():
    config = OmegaConf.load(Path(__file__).parent.parent.parent.parent / "mloq.yml")
    record = CMDRecord(config)
    command = SetupCMD(record=record)
    return command, config
