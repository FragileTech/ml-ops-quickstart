from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from omegaconf import DictConfig

from mloq.files import File


class Ledger:
    """Keep track of the generated files."""

    def __init__(self):
        """Initialize a new instance of the Ledger class."""
        self._files = []

    @property
    def files(self) -> List[Tuple[str, str]]:
        """Return the list of generated file names."""
        return [(str(f), d) for f, d in sorted(self._files)]

    def register(self, file: Union[File, str, Path], description: Optional[str] = None) -> None:
        """Append another generated file to the book."""
        if isinstance(file, File):
            description = file.description if description is None else description
            file = file.dst
        elif description is None:
            raise ValueError("description is None. Please provide a file description")
        self._files.append((Path(file), description))


class CMDRecord:
    """Keep track of files and directories that will be created by mloq."""

    def __init__(self, config: Optional[DictConfig] = None):
        """Initialize a new instance of the Ledger class."""
        self._files: Dict[Path, File] = {}
        self._directories: List[Path] = []
        self._config: DictConfig = DictConfig({}) if config is None else config

    @property
    def config(self) -> DictConfig:
        return self._config

    @property
    def files(self) -> Dict[Path, File]:
        return self._files

    @property
    def directories(self) -> List[Path]:
        return self._directories

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
