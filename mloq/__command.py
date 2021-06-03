from pathlib import Path
import sys
from typing import Optional, Union
from unittest.mock import patch

import click
import hydra
from omegaconf import DictConfig, OmegaConf

from mloq.__api import dump_ledger as dl
from mloq.failure import Failure
from mloq.files import File, Ledger
from mloq.version import __version__


def load_config(config_file, hydra_args):
    config_file = Path(config_file if config_file else "mloq.yml")  # FIXME
    hydra_args = ["--config-dir", str(config_file.parent)] + list(hydra_args)
    config = DictConfig({})

    @hydra.main(config_name=config_file.name)
    def load_config(loaded_config: DictConfig):
        nonlocal config
        config = loaded_config

    with patch("sys.argv", [sys.argv[0]] + list(hydra_args)):
        load_config()

    return config


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
    def __init__(
        self,
        config: DictConfig,
        output_directory: Union[Path, str],
        overwrite: bool,
        interactive: bool,
        only_config: bool,
        file: File,
        ledger: Ledger,
    ):

        self._config = config
        self._output_directory = Path(output_directory)
        self._overwrite = overwrite
        self._interactive = interactive
        self._only_config = only_config
        self._file = file
        self.ledger = ledger

    @property
    def config(self) -> DictConfig:
        return self._config

    @property
    def output_directory(self) -> Path:
        return self._output_directory

    @property
    def overwrite(self) -> bool:
        return self._overwrite

    @property
    def interactive(self) -> bool:
        return self._interactive

    @property
    def only_config(self) -> bool:
        return self._only_config

    @property
    def file(self) -> File:
        return self._file

    def __call__(self, ledger: Ledger = None):
        return self.run(ledger)

    # Run logic
    def run(self, ledger: Ledger) -> int:
        """
        Initialize a new project using ML Opts Quickstart.

        It calls a set of fundamental methods in order to generate the
        required files to configure a new project following ML Ops best
        practices. The execution order is the following:

        - Load the configuration provided by the user (either interactively
        or via a yaml file.
        - Requests if the user wants to generate a yaml file and overwrites
        the existing files.
        - Fill in templates based on the supplied configuration (if necessary).
        - Generate the needed folders and files following the configuration
        introduced by the user
        - Write the summary of the generated files.

        Args:
            ledger: Ledger object. Keeps track of the generated files.

        Returns:
            This method returns an integer value summarizing the success
                of the process.
        """
        self.ledger = Ledger() if ledger is None else self.ledger
        if not isinstance(self.ledger, Ledger):
            raise ValueError("Please specify a Ledger")
        self.load_config()
        self.yaml_overwrite()
        if self.only_config:
            return 0
        try:
            self.write_templates()
            self.create_directories()
            self.dump_ledger()
        except Failure as e:
            print(f"Failed to setup the project: {e}", file=sys.stderr)
            return 1
        return 0

    # Configurations
    def load_config(self) -> DictConfig:
        """
        Complete self.config based on user preferences.

        Fills in self.config key-values using the user-supplied entries.
        Such values can be provided interactively or via a configuration
        file.

        Returns:
            This function returns a DictConfig object summarizing the
                configuration used on MLOQ.
        """
        assert isinstance(self.interactive, bool)
        if self.interactive:
            welcome_message(extra=False)
            return self.interactive_config()
        else:
            return self.generate_config()

    def interactive_config(self):
        """Generate the configuration of the project interactively."""
        raise NotImplementedError

    def generate_config(self):
        """Generate the configuration of the project via a configuration file."""
        raise NotImplementedError

    # Create Directories and Files
    def create_directories(self) -> None:
        """Create the necessary folders for the project."""
        raise NotImplementedError

    def write_config(self, safe: bool = False) -> None:
        """Write self.config in a yaml file."""
        if safe:
            path = Path(self.output_directory)
            path = path / self.file.dst if path.is_dir() else path
        with open(path, "w") as f:
            OmegaConf.save(self.config, f)

    def yaml_overwrite(self) -> None:
        """
        Write the configuration of the project and overwrite existing files.

        Logic module. Asks if the user is interested in saving the
        configuration selected for the project into a yaml file. Then, it
        requests if the user wants to overwrite existing files.
        """
        if self.interactive and (
            self.only_config or click.confirm("Do you want to generate a mloq.yml file?")
        ):
            self.write_config(safe=True)
        if not self.overwrite and self.interactive:
            self._overwrite = click.confirm("Do you want to overwrite existing files?")

    # Complete templates
    def write_templates(self) -> None:
        """Create new file containing the rendered template found in source_path."""
        raise NotImplementedError

    # Ledger
    def dump_ledger(self) -> None:
        """Write the summary of the generated files."""
        dl(
            path=self.output_directory,
            config=self.config,
            ledger=self.ledger,
            overwrite=self.overwrite,
        )


class SetupCommand(Command):
    def __init__(
        self,
        config: DictConfig,
        output_directory: Union[Path, str],
        overwrite: bool,
        interactive: bool,
        only_config: bool,
        ledger: Ledger,
    ):
        from mloq.files import mloq_yml

        self._file = mloq_yml
        super().__init__(
            config=config,
            output_directory=output_directory,
            overwrite=overwrite,
            interactive=interactive,
            only_config=only_config,
            file=self._file,
            ledger=ledger,
        )

    # Configurations
    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        from mloq.cli.__setup_cmd import generate_config_interactive

        return generate_config_interactive(self.config)

    def generate_config(self) -> DictConfig:
        """Generate the configuration of the project via a configuration file."""
        from mloq.config.__setup_generation import generate_config

        return generate_config(self.config)

    # Complete templates
    def write_templates(self) -> None:
        """
        Create new files using rendered templates as basis.

        It generates new files for the project by filling in the rendered
        templates according to the information supplied by the user.
        Generated files:
        - Repository files
        - Workflow actions to the corresponding repository
        - Documentation files
        - Requirement files (according to the selected options)
        """
        from mloq.__api import setup_requirements, setup_root_files
        from mloq.__workflows import setup_workflow_template
        from mloq.config.__params import is_empty

        assert isinstance(self.config, DictConfig)
        path = Path(self.output_directory)
        try:
            setup_root_files(
                path=path,
                config=self.config,
                overwrite=self.overwrite,
                ledger=self.ledger,
            )
            if not is_empty(self.config.project.get("ci", "empty")):  # FIXME if not
                setup_workflow_template(
                    config=self.config,
                    root_path=path,
                    ledger=self.ledger,
                    overwrite=self.overwrite,
                )
            if self.config.project.get("docs", False):
                self.write_template_docs()  # FIXME write it explicitly?
            if not is_empty(self.config.project.get("requirements", "empty")):  # FIXME if not
                setup_requirements(
                    path=path,
                    config=self.config,
                    ledger=self.ledger,
                    lint=True,
                    test=True,
                    overwrite=self.overwrite,
                )
        except Failure as e:  # FIXME is correct?
            print(f"Failed to generate file: {e} using rendered templates", file=sys.stderr)

    def write_template_docs(self) -> None:
        """Generate documentation files using rendered templates as basis."""
        from mloq.files import DOCS_FILES
        from mloq.templating import write_template

        source_files = {"conf.txt", "index.md"}
        docs_path = Path(self.output_directory) / "docs"
        for file in DOCS_FILES:
            out_path = (docs_path / "source") if file.name in source_files else docs_path
            write_template(
                file,
                config=self.config,
                path=out_path,
                ledger=self.ledger,
                overwrite=self.overwrite,
            )

    # Create Directories and Files
    def create_directories(self) -> None:
        """
        Create necessary folders for the project.

        It generates the requested folders for the new project on the
        target path following the configuration introduced by the user.
        Generated folders:
        - Root project skeleton
        - Folder structure for using GitHub actions
        - Documentation directory structure
        - Git repository
        """
        from mloq.__skeleton import (
            create_docs_directories,
            create_github_actions_directories,
            create_project_skeleton,
        )
        from mloq.config.__params import is_empty
        from mloq.git import setup_git

        assert isinstance(self.config, DictConfig)
        path = Path(self.output_directory)
        _original_project_name = self.config.template.project_name
        self._config.template.project_name = self.config.template.project_name.replace("-", "_")
        try:
            create_project_skeleton(
                config=self.config,
                root_path=path,
                ledger=self.ledger,
                overwrite=self.overwrite,
            )
            if not is_empty(self.config.project.get("ci", "empty")):  # FIXME if not
                create_github_actions_directories(root_path=path)
            if self.config.project.get("docs", False):
                create_docs_directories(root_path=path)
            if self.config.project.git_init:
                setup_git(path=path, config=self.config)
        except Failure as e:
            print(f"Failed to create folder: {e}", file=sys.stderr)  # FIXME is correct?
        finally:
            self._config.template.project_name = _original_project_name


class DocsCommand(Command):
    def __init__(
        self,
        config: DictConfig,
        output_directory: Union[Path, str],
        overwrite: bool,
        interactive: bool,
        only_config: bool,
        ledger: Ledger,
    ):
        from mloq.files import docs_yml

        self._file = docs_yml
        super().__init__(
            config=config,
            output_directory=output_directory,
            overwrite=overwrite,
            interactive=interactive,
            only_config=only_config,
            file=self._file,
            ledger=ledger,
        )

    # Configurations
    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        from mloq.cli.__docs_cmd import generate_config_interactive

        return generate_config_interactive(self.config)

    def generate_config(self) -> DictConfig:
        """Generate the configuration of the project via a configuration file."""
        from mloq.config.__docs_generation import generate_config

        return generate_config(self.config)

    def load_config(self) -> DictConfig:
        """
        Complete self.config based on user preferences.

        Fills in self.config key-values using the user-supplied entries.
        Such values can be provided interactively or via a configuration
        file.

        Returns:
            This function returns a DictConfig object summarizing the
                configuration used on MLOQ.
        """
        assert isinstance(self.interactive, bool)
        if self.interactive:
            string = "This generates the necessary documentation for your new project."
            welcome_message(extra=True, string=string)
            return self.interactive_config()
        else:
            return self.generate_config()

    # Complete templates
    def write_templates(self) -> None:
        """
        Create new files using rendered templates as basis.

        It generates new files for the project by filling in the rendered
        templates according to the information supplied by the user.
        Generated files:
        - Repository files
        - Workflow actions to the corresponding repository
        - Documentation files
        - Requirement files (according to the selected options)
        """
        assert isinstance(self.config, DictConfig)
        path = Path(self.output_directory)
        try:
            if self.config.project.get("docs", False):
                self.write_template_docs()  # FIXME write it explicitly?
        except Failure as e:  # FIXME is correct?
            print(f"Failed to generate file: {e} using rendered templates", file=sys.stderr)

    def write_template_docs(self) -> None:
        """Generate documentation files using rendered templates as basis."""
        from mloq.files import DOCS_FILES
        from mloq.templating import write_template

        source_files = {"conf.txt", "index.md"}
        docs_path = Path(self.output_directory) / "docs"
        for file in DOCS_FILES:
            out_path = (docs_path / "source") if file.name in source_files else docs_path
            write_template(
                file,
                config=self.config,
                path=out_path,
                ledger=self.ledger,
                overwrite=self.overwrite,
            )

    # Create Directories and Files
    def create_directories(self) -> None:
        """
        Create necessary folders for the project.

        It generates the requested folders for the new project on the
        target path following the configuration introduced by the user.
        Generated folders:
        - Root project skeleton
        - Folder structure for using GitHub actions
        - Documentation directory structure
        - Git repository
        """
        from mloq.__skeleton import create_docs_directories

        assert isinstance(self.config, DictConfig)
        path = Path(self.output_directory)
        _original_project_name = self.config.template.project_name
        self._config.template.project_name = self.config.template.project_name.replace("-", "_")
        try:
            if self.config.project.get("docs", False):
                create_docs_directories(root_path=path)
        except Failure as e:
            print(f"Failed to create folder: {e}", file=sys.stderr)  # FIXME is correct?
        finally:
            self._config.template.project_name = _original_project_name
