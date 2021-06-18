from pathlib import Path
from typing import Tuple

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.files import DOCS_FILES
from mloq.params import BooleanParam, config_group, ConfigParam


_DOCS = [
    BooleanParam("disable", "Disable docs command?"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("description", "Short description of the project"),
    ConfigParam("author", "Author(s) of the project"),
    ConfigParam("copyright_year", "Year when the project started"),
    ConfigParam("copyright_holder", "Copyright holder"),
]


class DocsCMD(Command):
    name = "docs"
    files = tuple(DOCS_FILES)
    CONFIG = config_group("DOCS", _DOCS)

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
