from pathlib import Path
from typing import Tuple

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.files import WORKFLOW_FILES, push_python_wkf
from mloq.params import BooleanParam, config_group, ConfigParam, MultiChoiceParam


_CI = [
    BooleanParam("disable", "Disable ci command?"),
    BooleanParam("docker", "Test Docker container in the CI?"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("default_branch", "Default branch of the project"),
    ConfigParam("docker_org", "Name of your docker organization"),
    ConfigParam("bot_name", "Bot's GitHub login to push commits in CI"),
    ConfigParam("bot_email", "Bot account email"),
    ConfigParam("ci_python_version", "Primary Python version in GitHub Actions"),
    MultiChoiceParam(
            "python_versions",
            text="Supported python versions",
            choices=["3.6", "3.7", "3.8", "3.9"],
        ),
    ConfigParam("ubuntu_version", "Primary Ubuntu version in GitHub Actions"),
    ConfigParam("ci_extra", "Additional script in GitHub Actions before running the main tests"),
]


class CiCMD(Command):
    name = "ci"
    files = tuple(WORKFLOW_FILES)
    CONFIG = config_group("CI", _CI)

    @property
    def directories(self) -> Tuple[Path]:
        return tuple([Path(".github") / "workflows"])

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to set up continuous integration.")
        return self.parse_config()

    def record_files(self) -> None:
        self.record.register_file(file=push_python_wkf, path=Path(".github") / "workflows")
