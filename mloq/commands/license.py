from pathlib import Path

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.files import code_of_conduct, contributing, dco, LICENSES
from mloq.params import BooleanParam, config_group, ConfigParam


OPEN_SOURCE_FILES = [dco, contributing, code_of_conduct]

_LICENSE = [
    BooleanParam("disable", "Disable license command?"),
    BooleanParam("open_source", "Is the project Open Source?"),
    ConfigParam(
        "license",
        "Project license type",
        type=click.Choice(["MIT", "Apache-2.0", "GPL-3.0", "None"], case_sensitive=False),
    ),
    ConfigParam("copyright_year", "Year when the project started"),
    ConfigParam("copyright_holder", "Copyright holder"),
]


class LicenseCMD(Command):
    name = "license"
    files = tuple([file for file in LICENSES.values()] + OPEN_SOURCE_FILES)
    config = config_group("LICENSE", _LICENSE)
    LICENSES = LICENSES

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to generate the project license files.")
        return self.parse_config()

    def record_files(self) -> None:
        conf = self.record.config.license
        if conf.open_source:
            for file in OPEN_SOURCE_FILES:
                self.record.register_file(file=file, path=Path())
            license_file = self.LICENSES[conf.license]
            self.record.register_file(file=license_file, path=Path())
