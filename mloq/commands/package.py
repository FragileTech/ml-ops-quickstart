from pathlib import Path

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.files import pyproject_toml, setup_py
from mloq.params import BooleanParam, config_group, ConfigParam, MultiChoiceParam


PACKAGE_FILES = [pyproject_toml, setup_py]

_PACKAGE = [
    BooleanParam("disable", "Disable package command?"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("pyproject_extra", "Additional pyproject.toml configuration"),
    ConfigParam(
        "license",
        "Project license type",
        type=click.Choice(["MIT", "Apache-2.0", "GPL-3.0", "None"], case_sensitive=False),
    ),
    MultiChoiceParam(
        "python_versions",
        text="Supported python versions",
        choices=["3.6", "3.7", "3.8", "3.9"],
    ),
    MultiChoiceParam(
        "requirements",
        text="Project requirements",
        choices=["data-science", "data-viz", "torch", "tensorflow", "none"],
    ),
]


class PackageCMD(Command):
    name = "package"
    files = tuple(PACKAGE_FILES)
    CONFIG = config_group("PACKAGE", _PACKAGE)
    LICENSE_CLASSIFIERS = {
        "MIT": "License :: OSI Approved :: MIT License",
        "Apache-2.0": "License :: OSI Approved :: Apache Software License",
        "GPL-3.0": "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "proprietary": "License :: Other/Proprietary License",
    }

    def parse_config(self) -> DictConfig:
        conf = super(PackageCMD, self).parse_config()
        conf.license.license_classifier = self.LICENSE_CLASSIFIERS[
            conf.license.get("license", "proprietary")
        ]
        return conf

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to generate the packaging files.")
        return self.parse_config()

    def record_files(self) -> None:
        for file in self.files:
            self.record.register_file(file=file, path=Path())
