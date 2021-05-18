"""Command line interface for mloq."""

from pathlib import Path
import sys
from unittest.mock import patch

import click
import hydra
from omegaconf import DictConfig

from mloq.files import docs_yml, setup_yml


overwrite_opt = click.option(
    "--overwrite/--no-overwrite",
    "-o/ ",
    default=False,
    show_default=True,
    help="Value indicating whether to overwrite existing files.",
)
config_file_opt = click.option(
    "--filename",
    "-f",
    "config_file",
    default=None,
    show_default=True,
    help="Name of the repository config file",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
)
only_config_opt = click.option(
    "--only-config/--everything",
    "-c/ ",
    default=False,
    show_default=True,
    help="Value indicating whether to not generate all the files except mloq.yml.",
)
output_directory_arg = click.argument(
    "output_directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)

interactive_opt = click.option(
    "--interactive/--no-interactive",
    "-i/ ",
    default=False,
    show_default=True,
    help="If True the configuration values will be defined interactively on the command line.",
)


@click.group()
def cli():
    """Command line interface for ML Ops Quickstart."""
    pass


@cli.command(context_settings=dict(ignore_unknown_options=True))
@config_file_opt
@output_directory_arg
@overwrite_opt
@interactive_opt
@only_config_opt
@click.argument("hydra_args", nargs=-1, type=click.UNPROCESSED)
def setup(
    config_file: str,
    output_directory: str,
    overwrite: bool,
    only_config: bool,
    interactive: bool,
    hydra_args: str,
) -> None:
    """Entry point of `mloq setup`."""
    from mloq.cli.setup_cmd import setup_cmd

    config_file = Path(config_file) if config_file else setup_yml.src
    hydra_args = ["--config-dir", str(config_file.parent)] + list(hydra_args)
    config = DictConfig({})

    @hydra.main(config_name=config_file.name)
    def load_config(loaded_config: DictConfig):
        nonlocal config
        config = loaded_config

    with patch("sys.argv", [sys.argv[0]] + list(hydra_args)):
        load_config()

    exit(setup_cmd(config, output_directory, overwrite, interactive, only_config))


@cli.command(context_settings=dict(ignore_unknown_options=True))
@config_file_opt
@output_directory_arg
@overwrite_opt
@interactive_opt
@only_config_opt
@click.argument("hydra_args", nargs=-1, type=click.UNPROCESSED)
def docs(
    config_file: str,
    output_directory: str,
    overwrite: bool,
    only_config: bool,
    interactive: bool,
    hydra_args: str,
) -> None:
    """
    Entry point of `mloq docs`.

    Command line option of MLOQ. Generates the necessary documentation
    files for the project. Generated files:

    * 'docs' folder containing the documentation of the project, as well
    as the necessary tools to improve it.

    * Customizable commands for building the documentation (included in 'Makefile').

    * 'requirements-docs.txt' file containing the required libraries to
    generate the documentation.

    * 'conf.py' configuration file for sphinx and documentation plugins.

    * [Optional] 'mloq.yml' file describing the configuration options
    selected for this project.
    """
    from mloq.cli.docs_cmd import docs_cmd

    config_file = Path(config_file) if config_file else docs_yml.src
    hydra_args = ["--config-dir", str(config_file.parent)] + list(hydra_args)
    config = DictConfig({})

    @hydra.main(config_name=config_file.name)
    def load_config(loaded_config: DictConfig):
        nonlocal config
        config = loaded_config

    with patch("sys.argv", [sys.argv[0]] + list(hydra_args)):
        load_config()

    exit(docs_cmd(config, output_directory, overwrite, interactive, only_config))
