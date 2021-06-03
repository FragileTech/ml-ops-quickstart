from pathlib import Path
from typing import NamedTuple, Optional, Tuple

import click
from omegaconf import DictConfig

from mloq.writer import CMDRecord
from mloq.config import params
from mloq.files import DOCS_FILES, PROJECT_FILES
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


class GlobalsCMD(Command):
    name = "globals"
    CONFIG = params.GLOBALS
    files = tuple()

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("The following values will occur in several places in the generated files.")
        return self.parse_config()

    def parse_config(self) -> DictConfig:
        """Generate the configuration of the project via a configuration file."""
        config = self.record.config.globals
        for param_name in self.CONFIG._fields:
            if param_name == "project_url":
                default_url = (
                    f"https://github.com/{config.owner}/{config.project_name.replace(' ', '-')}"
                )
                config.project_url = self.CONFIG.project_url(
                    config, self.interactive, default=default_url
                )
            else:
                value = getattr(self.CONFIG, param_name)(config, self.interactive)
                setattr(config, param_name, value)
        return self.record.config

    def record_files(self) -> None:
        pass


class ProjectCMD(Command):
    name = "project"
    files = tuple(PROJECT_FILES)
    CONFIG = params.PROJECT

    @property
    def directories(self) -> Tuple[Path]:
        project_folder = self.record.config.project.project_name.replace(" ", "_")
        return tuple([Path(project_folder) / "tests"])

    def record_files(self) -> None:
        from mloq.files import init, main, makefile, readme, test_main, version

        self.record.register_file(file=readme, path=Path())
        self.record.register_file(file=makefile, path=Path())
        project_folder = Path(self.record.config.project.project_name.replace(" ", "_"))
        description = "Python package header for the project module"
        self.record.register_file(file=init, path=project_folder, description=description)
        self.record.register_file(file=main, path=project_folder)
        self.record.register_file(file=version, path=project_folder)
        description = "Python package header for the test module"
        self.record.register_file(file=init, path=project_folder / "test", description=description)
        self.record.register_file(file=test_main, path=project_folder / "test")


class DocsCMD(Command):
    name = "docs"
    files = tuple(DOCS_FILES)
    CONFIG = params.DOCS

    @property
    def directories(self) -> Tuple[Path]:
        return tuple([Path("docs") / "source" / "markdown"])

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to generate the project documentation.")
        return self.parse_config()

    def record_files(self) -> None:
        source_files = {"conf.py", "index.md"}
        docs_path = Path("docs")
        for file in self.files:
            path = (docs_path / "source") if str(file.dst) in source_files else docs_path
            self.record.register_file(file=file, path=path)
