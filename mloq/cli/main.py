"""Command line interface for mloq."""

import os
from pathlib import Path
import sys
from unittest.mock import patch

import click
import hydra
from omegaconf import DictConfig

from mloq.files import mloq_yml

overwrite_opt = click.option(
    "--overwrite/--no-overwrite",
    "-o/ ",
    default=False,
    show_default=True,
    help="If True overwrite existing files. If False ignore files that already exist.",
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


def _parse_env(config_file, override, interactive):
    """Parse environment variables defining command options."""
    config_file = os.getenv("MLOQ_CONFIG_FILE", config_file)
    override = os.getenv("MLOQ_OVERRIDE", override)
    interactive = os.getenv("MLOQ_INTERACTIVE", interactive)
    return config_file, override, interactive


@click.group()
def cli():
    """Command line interface for ML Ops Quickstart."""
    pass


@cli.command(context_settings=dict(ignore_unknown_options=True))
@config_file_opt
@output_directory_arg
@overwrite_opt
@interactive_opt
@click.argument("hydra_args", nargs=-1, type=click.UNPROCESSED)
def setup(
    config_file: str,
    output_directory: str,
    overwrite: bool,
    interactive: bool,
    hydra_args: str,
) -> None:
    """Entry point of `mloq setup`."""
    from mloq.cli.setup_cmd import setup_cmd

    config_file = Path(config_file) if config_file else mloq_yml.src
    hydra_args = ["--config-dir", str(config_file.parent)] + list(hydra_args)
    config = DictConfig({})

    @hydra.main(config_name=config_file.name)
    def load_config(loaded_config: DictConfig):
        nonlocal config
        config = loaded_config

    with patch("sys.argv", [sys.argv[0]] + list(hydra_args)):
        load_config()

    exit(setup_cmd(config, output_directory, overwrite, interactive))
