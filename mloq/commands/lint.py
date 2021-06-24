from pathlib import Path

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.files import pyproject_toml, lint_req
from mloq.params import BooleanParam, config_group, ConfigParam


PACKAGE_FILES = [pyproject_toml, lint_req]

_LINT = [
    BooleanParam("disable", "Disable package command?"),
    BooleanParam("docstring_checks", "Disable package command?"),
    ConfigParam("pyproject_extra", "Additional pyproject.toml configuration"),
]


class LintCMD(Command):
    name = "lint"
    files = tuple(PACKAGE_FILES)
    CONFIG = config_group("LINT", _LINT)

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to generate the packaging files.")
        return self.parse_config()

    def record_files(self) -> None:
        for file in self.files:
            self.record.register_file(file=file, path=Path())
