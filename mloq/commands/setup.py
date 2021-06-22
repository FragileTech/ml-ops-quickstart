from pathlib import Path
from typing import List, Tuple

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.files import conf_py, docs_req, index_md, make_bat_docs, makefile_docs
from mloq.params import config_group
from mloq.record import CMDRecord


def _sub_commands():
    from mloq.commands import CiCMD, DocsCMD, GlobalsCMD, LicenseCMD, LintCMD, ProjectCMD

    return CiCMD, DocsCMD, GlobalsCMD, LicenseCMD, LintCMD, ProjectCMD, ProjectCMD


SUB_COMMANDS = _sub_commands()
DOCS_FILES = [conf_py, index_md, makefile_docs, make_bat_docs, docs_req]

_SETUP = list(set([param for cmd in SUB_COMMANDS for param in cmd.CONFIG]))


class SetupCMD(Command):
    name = "setup"
    files = tuple([file for cmd in SUB_COMMANDS for file in cmd.files])
    # CONFIG = config_group("SETUP", _SETUP)
    SUB_COMMAND_CLASSES = SUB_COMMANDS

    def __init__(self, record: CMDRecord, interactive: bool = False):
        super(SetupCMD, self).__init__(record=record, interactive=interactive)
        self._sub_commands = [
            cmd(record=self.record, interactive=interactive) for cmd in self.SUB_COMMAND_CLASSES
        ]

    @property
    def sub_commands(self) -> List[Command]:
        return self._sub_commands

    @property
    def directories(self) -> Tuple[Path]:
        return tuple([directory for cmd in self.sub_commands for directory in cmd.directories])

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to generate the project configuration.")
        return self.parse_config()

    def parse_config(self) -> DictConfig:
        for cmd in self.sub_commands:
            self.record.update_config(cmd.parse_config())
        return self.record.config

    def record_files(self) -> None:
        for cmd in self.sub_commands:
            cmd.record_files()
