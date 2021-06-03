import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from omegaconf import DictConfig

from mloq import _logger
from mloq.files import File, Ledger
from mloq.templating import render_template


class CMDRecord:
    """Keep track of files and directories that will be created by mloq."""

    def __init__(self, config: Optional[DictConfig] = None):
        """Initialize a new instance of the Ledger class."""
        self.files: Dict[Path, File] = {}
        self.directories: List[Path] = []
        self._config: DictConfig = DictConfig({}) if config is None else config

    @property
    def config(self) -> DictConfig:
        return self._config

    def update_config(self, config: DictConfig) -> None:
        self._config = config

    def register_file(
        self,
        file: File,
        path: Union[Path, str],
        description: Optional[str] = None,
    ) -> None:
        """Append another generated file to the book."""
        if description is None and not file.description:
            raise ValueError("File description cannot be None. Please provide a description.")
        elif description is not None:
            file = File(
                name=file.name,
                src=file.src,
                dst=file.dst,
                description=description,
                is_static=file.is_static,
            )
        self.files[Path(path) / file.dst] = file

    def register_directory(self, path: Union[Path, str]) -> None:
        self.directories.append(Path(path))


class Writer:
    """Write all the files specified on the provided CMDRecord."""

    def __init__(self, path: Union[Path, str], record: CMDRecord, overwrite: bool = False):
        self._record = record
        self._ledger = Ledger()
        self._path = Path(path)  # Path to the project root directory
        self.overwrite = overwrite

    @property
    def path(self) -> Path:
        return self._path

    @property
    def ledger(self) -> Ledger:
        return self._ledger

    @property
    def record(self) -> CMDRecord:
        return self._record

    def create_directories(self) -> None:
        for directory in self.record.directories:
            os.makedirs(self.path / directory, exist_ok=True)

    def write_templates(self) -> None:
        for path, file in self.record.files.items():
            self.write_template(file=file, path=path, config=self.record.config)

    def dump_ledger(self) -> None:
        raise NotImplementedError

    def write_template(
        self,
        file: File,
        path: Path,
        config: DictConfig,
    ) -> None:
        """
        Create new file containing the rendered template found in source_path.

        Args:
            file: File object representing the jinja template that will be rendered.

        Returns:
            None.
        """
        path = self.path / path
        if not self.overwrite and path.exists():
            _logger.debug(f"file {file.dst} already exists. Skipping")
            return

        self.ledger.register(file, description=file.description)
        rendered = render_template(file, config)
        with open(path, "w") as f:
            f.write(rendered)

    def run(self) -> None:
        self.create_directories()
        self.write_templates()
        self.dump_ledger()
