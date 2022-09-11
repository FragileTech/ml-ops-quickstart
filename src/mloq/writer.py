"""The writer module defines the Writer class, which is in charge of creating the files \
and directories specified in the CMDRecord."""
import os
from pathlib import Path
from typing import Union

from omegaconf import DictConfig

from mloq.files import File, what_mloq_generated
from mloq.record import CMDRecord, Ledger
from mloq.templating import write_template


class Writer:
    """
    Write all the files specified on the provided CMDRecord.

    This class fills in rendered templates according to the provided
    configuration and generates the resulting file on the specified
    folder.

    Attributes of this class:
        path: Path string describing the destination folder where the
            file will be created.
        ledger: Instance of the Ledger class. It contains a dictionary
            summarizing the files that will by generated by mloq.
        record: Instance of the CMDRecord class. It keeps track of all
            files and directories that will be created from the
            user's configuration.
        overwrite: Boolean value. If True, existing files will be rewritten
            by mloq application.
    """

    def __init__(self, path: Union[Path, str], record: CMDRecord, overwrite: bool = False):
        """
        Initialize a new instance of the CMDRecord class.

        The class is instantiated from a CMDRecord object, which keeps
        of all files and directories that will be created by mloq.

        Args:
            path: Path string describing the location where the files
                will be generated.
            record: CMDRecord instance. Register the files and directories
                that will be created by mloq according to the configuration
                provided by the user.
            overwrite: Boolean value. If True, all existing files will be
                rewritten by the mloq application.
        """
        self._record = record
        self._ledger = Ledger()
        self._path = Path(path)  # Path to the project root directory
        self.overwrite = overwrite

    @property
    def path(self) -> Path:
        """Path string describing the location where the files will be generated."""
        return self._path

    @property
    def ledger(self) -> Ledger:
        """Keep track of the generated files."""
        return self._ledger

    @property
    def record(self) -> CMDRecord:
        """Register the files and directories generated by the mloq application."""
        return self._record

    def create_directories(self) -> None:
        """Create the folders registered inside the attribute 'record.directories'."""
        for directory in self.record.directories:
            os.makedirs(self.path / directory, exist_ok=True)

    def write_templates(self) -> None:
        """Generate the files recorded in the attribute 'record.files' on the specified path."""
        for path, file in self.record.files.items():
            self.write_template(file=file, path=path, config=self.record.config)

    def dump_ledger(self) -> None:
        """
        Write the summary of the generated files.

        This method collects the elements stored in ledger to create a markdown
        document that summarizes all the files generated by the MLOQ application.
        """
        config = DictConfig({**self.record.config, "generated_files": self.ledger.files})
        self.write_template(
            what_mloq_generated,
            path=what_mloq_generated.dst,
            config=config,
        )

    def write_template(
        self,
        file: File,
        path: Path,
        config: DictConfig,
    ) -> None:
        """
        Create new file containing the rendered template configuration.

        Args:
            file: File object representing the jinja template that will be rendered.
            path: Target folder where the generated files will be written.
            config: DictConfig containing the selected project configuration.

        Returns:
            None.
        """
        write_template(
            file=file,
            config=config,
            path=self.path / path,
            overwrite=self.overwrite,
            ledger=self.ledger,
        )

    def run(self) -> None:
        """Generate all files and directories registered inside the record instance."""
        self.create_directories()
        self.write_templates()
        self.dump_ledger()