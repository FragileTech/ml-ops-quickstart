"""This module contains the classes that keep track of the internal state of the\
 application when running a Command."""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from omegaconf import DictConfig, OmegaConf

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
    """
    Keep track of files and directories that will be created by mloq.

    The :class:`CMDRecord` acts as a single source of truth for storing the
    files and directories generated by `mloq` as well as the necessary configuration
    to generate them.

    This class registers three separate data sources:

    - `config`:
        An :class:`omegaconf.DictConfig` that contains the configuration of
        all the commands executed by `mloq`.

    - `files`:
        A `dict` containing the content and location of the files generated by mloq.
        It is indexed by :class:`Path` objects that indicate where the file will be created, and
        its values are instances of :class:`mloq.files.File`.

    - `directories`:
        List of :class:`Path` instances pointing to the different directories
        that `mloq` will create.

    This class is initialized from a configuration dictionary. The dictionary
    can be either an :class:`omegaconf.DictConfig` or an empty dictionary.
    """

    def __init__(
        self,
        config: Optional[DictConfig] = None,
        files: Optional[Dict[Path, File]] = None,
        directories: Optional[List[Path]] = None,
    ):
        """
        Initialize a new instance of :class:`CMDRecord`.

        Args:
           config: DictConfig element that stores the configuration parameters.
            files: Dictionary that registers the files generated by mloq. Keys
                are Paths strings labeling the location where the file will
                be created. Values are File elements referencing the current
                file.
            directories: List that stores the directories that will be generated
                by the mloq according to the user's configuration.
        """
        self._files = {} if files is None else files
        self._directories: List[Path] = [] if directories is None else directories
        self._config: DictConfig = DictConfig({}) if config is None else config

    @property
    def config(self) -> DictConfig:
        """
        Store the configuration parameters that govern the project's structure.

        It contains one configuration entry per each :class:`Command` that will be run,
        and each entry will only be modified by the :class:`Command` it represents. Each
        :class:`Command` instance is responsible for updating its corresponding
        `config` values.

        Returns:
             :class:`omegaconf.DictConfig` that contains the configuration of
             all the commands executed by `mloq`.
        """
        return self._config

    @property
    def files(self) -> Dict[Path, File]:
        """
        Return the dictionary of files used by mloq to generate the project configuration.

        `files` is a `dict` containing the content and location of the files generated by mloq.
        It is indexed by :class:`Path` objects that indicate where the file will be created, and
        its values are instances of :class:`mloq.files.File`.

        Each different :class:`Command` is responsible for registering the files it generates
        to the `files` dictionary.
        """
        return self._files

    @property
    def directories(self) -> List[Path]:
        """Contain the folders that will be created by mloq for storing the project's files."""
        return self._directories

    def update_config(self, config: DictConfig) -> None:
        """Update the configuration attribute according to the values entered by the user."""
        self._config = OmegaConf.merge(self._config, config)

    def register_file(
        self,
        file: File,
        path: Union[Path, str],
        description: Optional[str] = None,
    ) -> None:
        """
        Append a new file to the 'files' container.

        Keys are Path strings describing the location where the file will
        be created. Values are File objects containing the information
        of the file that will be generated.
        """
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
        """Append a new directory path to the 'directories' container."""
        self.directories.append(Path(path))
