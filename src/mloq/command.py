"""This module defines the base Command class used for defining mloq commands."""
from pathlib import Path
from typing import Tuple

from omegaconf import DictConfig

from mloq.config.configuration import as_resolved_dict
from mloq.config.prompt import Promptable
from mloq.writer import CMDRecord


class CommandMixin:
    """Class containing the interface for defining an MLOQ Command."""

    files: tuple = tuple()
    cmd_name = "command"

    def __init__(self, record: CMDRecord, interactive: bool = False, *args, **kwargs):
        """
        Instantiate the Command class.

        Args:
            record: CMDRecord instance. Keeps a record of the user's
                configuration. It registers the files and directories
                that will be generated by mloq.
            interactive: Boolean value. If True, configuration values are
                introduced interactively. Otherwise, the configuration is
                parsed from a user-generated configuration file.
        """
        self._record = record
        self.interactive = interactive
        super().__init__(*args, **kwargs)

    @property
    def record(self) -> CMDRecord:
        """Return a CMDRecord that keeps track of the files and directories the command creates."""
        return self._record

    @property
    def directories(self) -> Tuple[Path]:
        """
        Tuple containing Paths objects representing the directories the Command creates.

        Override this property if your command creates any directories.

        Returns:
            Tuple of :class:`Path` objects representing the path to the directories that the
            :class:`Command` will create.
        """
        return tuple()

    def parse_config(self) -> DictConfig:
        """
        Update the configuration dictionary from the data entered by the user.

        Given the basic configuration skeleton (contained in mloq.yaml), \
        this method updates the values of those parameters (included in \
        CONFIG object) that are related to the selected command. Incoming \
        values are introduced either interactively or via a custom user's \
        mloq.yaml file.

        Returns:
            It returns an updated version of the 'config' attribute of \
            the 'record' instance.
        """
        self.record.update_config(DictConfig({self.cmd_name: self.config}))
        return self.record.config

    def interactive_config(self) -> DictConfig:
        """Pass user's configuration interactively."""
        raise NotImplementedError

    def record_files(self) -> None:
        """Register the files that will be generated by mloq."""
        if len(self.files) > 0:
            raise NotImplementedError

    def record_directories(self) -> None:
        """Register the directories that will be generated by mloq."""
        for directory in self.directories:
            self._record.register_directory(directory)

    def configure(self) -> None:
        """
        Save the updated version of the 'config' attribute.

        After parsing the new configuration values introduced by the user,
        this method registers and saves this updated configuration within
        the '_config' attribute of the 'record' instance.
        """
        if self.interactive:
            self.interactive_config()
            # config = self.interactive_config()
        else:
            self.parse_config()
            # config = self.parse_config()
        # self.record.update_config(config)

    def run_side_effects(self) -> None:
        """Apply additional configuration methods."""
        pass

    def run(self) -> CMDRecord:
        """
        Record the files and directories generated by mloq according to the user's configuration.

        This method updates the configuration dictionary with the values
        introduced by the user. Once the parameters have been revised,
        the files and directories that will be generated by mloq are
        registered within the 'record' instance.

        Returns:
            It returns an updated version of the CMDRecord instance, where
                the files and directories that will be generated by mloq
                are recorded within the 'record' instance.
        """
        self.configure()
        self.record_directories()
        self.record_files()
        self.run_side_effects()
        return self.record


class Command(CommandMixin, Promptable):
    """
    Define blueprints for generating custom mloq commands.

    Base class used for defining new mloq commands. It establishes the
    fundamental methods for defining and updating the configuration values
    used to create the necessary files for the user's project, while
    registering the latter for later use.

    This class is initialized from a CMDRecord instance, object where the
    user's configuration, as well as the files and directories that will
    be generated, are stored.

    class Attributes:
        name: Name of the command.
        files: Tuple containing the templates used for creating the \
               necessary files of your project.
        CONFIG: NamedTuple containing the keys and values of your \
                configuration RELATIVE to the command.
    """

    def __init__(self, record: CMDRecord, interactive: bool = False, **kwargs):
        """
        Instantiate the Command class.

        Args:
            record: CMDRecord instance. Keeps a record of the user's
                configuration. It registers the files and directories
                that will be generated by mloq.
            interactive: Boolean value. If True, configuration values are
                introduced interactively. Otherwise, the configuration is
                parsed from a user-generated configuration file.
            cfg_node: key of the DictConfig in record that contains the configuration
                      of the current command.
        """
        # self._record = record
        # self.interactive = interactive
        # TODO: allow interpolations in config that refer to the global record config
        # cmd_conf = self._config_from_record()
        # cfg_node = self.cmd_name if cfg_node is None else cfg_node
        super(Command, self).__init__(
            record=record,
            interactive=interactive,
            config=record.config,
            cfg_node=self.cmd_name,
            **kwargs,
        )

    def interactive_config(self) -> DictConfig:
        """Pass user's configuration interactively."""
        prompt_conf = DictConfig({self.cmd_name: self.prompt.prompt_all()})
        self.record.update_config(prompt_conf)
        return self.record.config

    def _config_from_record(self) -> DictConfig:
        return DictConfig(as_resolved_dict(self.record.config))[self.cmd_name]
