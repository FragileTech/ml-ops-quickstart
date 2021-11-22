"""Mloq ci command implementation."""
from pathlib import Path
from typing import Tuple

import click
from omegaconf import DictConfig
import param

from mloq.command import Command
from mloq.files import push_python_wkf


WORKFLOW_FILES = [push_python_wkf]

PYTHON_VERSIONS = ["3.6", "3.7", "3.8", "3.9"]


class CiCMD(Command):
    """Implement the functionality of the ci Command."""

    cmd_name: str = "ci"
    ubuntu_version = param.String(doc="Primary Ubuntu version in GitHub Actions")
    disable = param.Boolean(default=False, doc="Disable ci command?")
    docker = param.Boolean(doc="Test Docker container in the CI?")
    project_name = param.String("${globals.project_name}", doc="Select project name")
    default_branch = param.String(doc="Default branch of the project")
    docker_org = param.String(doc="Name of your docker organization")
    bot_name = param.String(doc="Bot's GitHub login to push commits in CI")
    bot_email = param.String(doc="Bot account email")
    ci_python_version = param.String(doc="Primary Python version in GitHub Actions")
    python_versions = param.ListSelector(
        default=PYTHON_VERSIONS,
        doc="Supported python versions",
        objects=PYTHON_VERSIONS,
    )
    ci_extra = param.String(
        doc="Additional script in GitHub Actions before running the main tests",
    )
    vendor = param.String(doc="Continuous Integration Vendor")
    open_source = param.Boolean(doc="Is the project Open Source?")
    author = param.String(doc="Author(s) of the project")
    owner = param.String("${ci.author}", doc="Github handle of the project owner")
    email = param.String(doc="Owner contact email")
    project_url = param.String(doc="GitHub project url")
    files = tuple(WORKFLOW_FILES)

    @property
    def directories(self) -> Tuple[Path]:
        """Tuple containing Paths objects representing the directories created by the command."""
        return tuple([Path(".github") / "workflows"])

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to set up continuous integration.")
        return super(CiCMD, self).interactive_config()

    def record_files(self) -> None:
        """Register the files that will be generated by mloq."""
        self.record.register_file(file=push_python_wkf, path=Path(".github") / "workflows")
