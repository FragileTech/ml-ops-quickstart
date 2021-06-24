from pathlib import Path
from typing import List, Tuple

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.record import CMDRecord


def _sub_commands():
    from mloq.commands import (
        CiCMD,
        DocsCMD,
        GlobalsCMD,
        LicenseCMD,
        LintCMD,
        ProjectCMD,
        RequirementsCMD,
    )

    return CiCMD, DocsCMD, GlobalsCMD, LicenseCMD, LintCMD, ProjectCMD, ProjectCMD, RequirementsCMD


SUB_COMMANDS = _sub_commands()

_SETUP = list(set([param for cmd in SUB_COMMANDS for param in cmd.CONFIG]))


class SetupCMD(Command):
    name = "setup"
    files = tuple([file for cmd in SUB_COMMANDS for file in cmd.files])
    SUB_COMMAND_CLASSES = SUB_COMMANDS

    def __init__(self, record: CMDRecord, interactive: bool = False):
        super(SetupCMD, self).__init__(record=record, interactive=interactive)
        self._sub_commands = [
            cmd(record=self.record, interactive=interactive) for cmd in self.SUB_COMMAND_CLASSES
        ]
        self.files = tuple([file for cmd in self._sub_commands for file in cmd.files])

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
