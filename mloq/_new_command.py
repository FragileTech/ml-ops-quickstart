from pathlib import Path
import sys
from typing import Optional, Union
from unittest.mock import patch

import click
import hydra
from omegaconf import DictConfig, OmegaConf

from mloq._writer import CMDRecord
from mloq.api import dump_ledger as dl
from mloq.failure import Failure
from mloq.files import DOCS_FILES, File, Ledger
from mloq.version import __version__


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
    files = []

    def __init__(self, record: CMDRecord, interactive: bool = False):
        self._record = record
        self._interactive = interactive

    @property
    def record(self) -> CMDRecord:
        return self._record

    def interactive_config(self) -> DictConfig:
        raise NotImplementedError

    def parse_config(self) -> DictConfig:
        raise NotImplementedError

    def record_directories(self) -> None:
        raise NotImplementedError

    def record_files(self) -> None:
        raise NotImplementedError

    def configure(self) -> None:
        if self._interactive:
            config = self.interactive_config()
        else:
            config = self.parse_config()
        self.record.update_config(config)

    def run(self) -> CMDRecord:
        self.configure()
        self.record_directories()
        self.record_files()
        return self.record


class DocsCommand(Command):
    name = "docs"
    files = DOCS_FILES

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        from mloq.cli.docs_cmd import generate_config_interactive

        string = "This generates the necessary documentation for your new project."
        welcome_message(extra=True, string=string)
        return generate_config_interactive(self.record.config)

    def parse_config(self) -> DictConfig:
        """Generate the configuration of the project via a configuration file."""
        from mloq.config.docs_generation import generate_config

        return generate_config(self._record.config)

    def record_directories(self) -> None:
        docs_dirs = Path("docs") / "source" / "markdown"
        self._record.register_directory(docs_dirs)

    def record_files(self) -> None:
        source_files = {"conf.py", "index.md"}
        docs_path = Path("docs")
        for file in self.files:
            path = (docs_path / "source") if file.dst in source_files else docs_path
            self.record.register_file(file=file, path=path)
