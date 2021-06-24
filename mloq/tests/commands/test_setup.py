from pathlib import Path

from omegaconf import OmegaConf
import pytest

from mloq.commands.setup import SetupCMD
from mloq.tests.test_command import command_and_example, TestCommand
from mloq.writer import CMDRecord


@pytest.fixture(scope="function")
def command_and_config():
    config = OmegaConf.load(Path(__file__).parent.parent / "examples" / "mloq.yml")
    record = CMDRecord(config)
    command = SetupCMD(record=record)
    return command, config
