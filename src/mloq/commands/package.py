"""Mloq package command implementation."""
from pathlib import Path

import click
from omegaconf import DictConfig, MISSING, OmegaConf

from mloq.command import Command
from mloq.config.param_patch import param
from mloq.files import ASSETS_PATH, file, pyproject_toml


PACKAGE_ASSETS_PATH = ASSETS_PATH / "package"
PYTHON_VERSIONS = ["3.6", "3.7", "3.8", "3.9", "3.10"]
DEFAULT_PYTHON_VERSIONS = ["3.7", "3.8", "3.9", "3.10"]
setup_py = file(
    "setup.txt",
    PACKAGE_ASSETS_PATH,
    "Python package installation metadata",
    dst="setup.py",
)
PACKAGE_FILES = [pyproject_toml, setup_py]


class PackageCMD(Command):
    """Implement the functionality of the package Command."""

    cmd_name = "package"
    files = tuple(PACKAGE_FILES)
    LICENSE_CLASSIFIERS = {
        "MIT": "License :: OSI Approved :: MIT License",
        "Apache-2.0": "License :: OSI Approved :: Apache Software License",
        "GPL-3.0": "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "proprietary": "License :: Other/Proprietary License",
    }
    disable = param.Boolean(default=None, doc="Disable package command?")
    pyproject_extra = param.String("", doc="Additional pyproject.toml configuration")
    project_name = param.String("${globals.project_name}", doc="Select project name")
    license = param.String("MIT", doc="Project license type")
    license_classifier = param.String(MISSING, doc="License classifier in setup.py")
    description = param.String("${globals.description}", doc="Short description of the project")
    default_branch = param.String(doc="Default branch of the project")
    project_url = param.String("${globals.project_url}", doc="GitHub project url")
    owner = param.String("${ci.author}", doc="Github handle of the project owner")
    author = param.String(doc="Author(s) of the project")
    email = param.String(doc="Owner contact email")
    python_versions = param.ListSelector(
        default=DEFAULT_PYTHON_VERSIONS,
        doc="Supported python versions",
        objects=PYTHON_VERSIONS,
    )
    use_poetry = param.Boolean("${globals.use_poetry}", doc="Add pipenv support to the project configuration")

    def parse_config(self) -> DictConfig:
        """Update the configuration DictConfig with the Command parameters."""
        conf = super(PackageCMD, self).parse_config()
        if OmegaConf.is_missing(conf.package, "license_classifier"):
            conf.package.license_classifier = self.LICENSE_CLASSIFIERS[
                conf.package.get("license", "proprietary")
            ]
        return conf

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to generate the packaging files.")
        return self.parse_config()

    def record_files(self) -> None:
        """Register the files that will be generated by mloq."""
        for _file in self.files:
            self.record.register_file(file=_file, path=Path())
