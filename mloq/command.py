from pathlib import Path
from typing import NamedTuple, Optional, Tuple

import click
from omegaconf import DictConfig

from mloq import params
from mloq.files import DOCS_FILES, PROJECT_FILES
from mloq.version import __version__
from mloq.writer import CMDRecord


def welcome_message(extra: bool = False, string: Optional[str] = None):
    """Welcome message to be displayed during interactive setup."""
    click.echo(f"Welcome to the MLOQ {__version__} interactive setup utility.")
    if extra:
        click.echo(f"{string}")
    click.echo()
    click.echo(
        "Please enter values for the following settings (just press Enter "
        "to accept a default value, if one is given in brackets).",
    )
    click.echo()


class Command:
    name = ""
    files = tuple()
    CONFIG: NamedTuple = NamedTuple("Config", [])()

    def __init__(self, record: CMDRecord, interactive: bool = False):
        self._record = record
        self.interactive = interactive

    @property
    def record(self) -> CMDRecord:
        return self._record

    @property
    def directories(self) -> Tuple[Path]:
        return tuple()

    def parse_config(self) -> DictConfig:
        config = getattr(self.record.config, self.name)  # TODO: gestionar caso de config vacio.
        for param_name in self.CONFIG._fields:
            value = getattr(self.CONFIG, param_name)(config, self.interactive)
            setattr(config, param_name, value)
        return self.record.config

    def interactive_config(self) -> DictConfig:
        return self.parse_config()

    def record_files(self) -> None:
        if len(self.files) > 0:
            raise NotImplementedError

    def record_directories(self) -> None:
        for directory in self.directories:
            self._record.register_directory(directory)

    def configure(self) -> None:
        if self.interactive:
            config = self.interactive_config()
        else:
            config = self.parse_config()
        self.record.update_config(config)

    def run(self) -> CMDRecord:
        self.configure()
        self.record_directories()
        self.record_files()
        return self.record
