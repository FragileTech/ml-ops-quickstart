"""Mloq lint command implementation."""
from pathlib import Path

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.config.param_patch import param
from mloq.files import lint_req, pyproject_toml


PACKAGE_FILES = [pyproject_toml, lint_req]


class LintCMD(Command):
    """Implement the functionality of the lint Command."""

    cmd_name = "lint"
    files = tuple(PACKAGE_FILES)
    disable = param.Boolean(default=None, doc="Disable lint command?")
    docstring_checks = param.Boolean(True, doc="Apply docstring checks?")
    pyproject_extra = param.String("", doc="Additional pyproject.toml configuration")
    project_name = param.String(doc="Select project name")
    makefile = param.Boolean(True, doc="Add check and style commands to makefile")

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to generate the packaging files.")
        return self.parse_config()

    def record_files(self) -> None:
        """Register the files that will be generated by mloq."""
        for file in self.files:
            self.record.register_file(file=file, path=Path())
