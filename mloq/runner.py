"""This module defines the pipeline for running a mloq command, such as config loading, \
template writing and interfacing with click."""
from pathlib import Path
import sys
from typing import Callable, Union
from unittest.mock import patch

import hydra
from omegaconf import DictConfig, OmegaConf

from mloq import _logger
from mloq.command import Command
from mloq.files import mloq_yml
from mloq.record import CMDRecord
from mloq.writer import Writer


def load_config(config_file: Union[Path, str], hydra_args: str) -> DictConfig:
    """
    Load the necessary configuration for running mloq from a mloq.yaml file.

    If no path to mloq.yaml is provided, it returns a template to be filled in
    using the interactive mode.

    Args:
        config_file: Path to the target mloq.yaml file.
        hydra_args: Arguments passed to hydra for composing the project configuration.

    Returns:
        DictConfig containing the project configuration.
    """
    config_file = Path(config_file) if config_file else Path() / mloq_yml.dst
    config_file = (
        config_file
        if (config_file.exists() and config_file.is_file())
        else config_file / mloq_yml.dst
    )
    if config_file.exists() and config_file.is_file():
        _logger.info(f"Loading config file from {config_file}")
        hydra_args = ["--config-dir", str(config_file.parent)] + list(hydra_args)
        config = DictConfig({})

        @hydra.main(config_path=".", config_name=config_file.name)
        def load_config(loaded_config: DictConfig):
            nonlocal config
            config = loaded_config

        with patch("sys.argv", [sys.argv[0]] + list(hydra_args)):
            load_config()
    else:
        _logger.info("No mloq.yaml file provided. Creating a new configuration")
        config = OmegaConf.load(mloq_yml.src)
    return config


def write_record(
    record: CMDRecord,
    path: Union[Path, str],
    overwrite: bool = False,
    only_config: bool = False,
) -> None:
    """
    Write the contents of the provided record to the target path.

    The writing process is performed by :class: `Writer`, class that fills
    in rendered templates according to the given configuration.

    Args:
        record: CMDRecord containing all the data to be written.
        path: Target directory to write the data.
        overwrite: If True overwrite existing files.
        only_config: Do not write any file except mloq.yaml

    Returns:
        None.
    """
    if only_config:
        with open(Path(path) / mloq_yml.dst, "w") as f:
            OmegaConf.save(config=record.config, f=f)
    else:
        writer = Writer(record=record, overwrite=overwrite, path=path)
        writer.run()


def run_command(cmd_cls, use_click: bool = True) -> Callable:
    """
    Run the given Command class.

    Args:
        cmd_cls: Command to be executed.
        use_click: If True run the function as a "cli" command.

    Returns:
        A function that will run the target class as a mloq command.
    """
    from mloq.cli import mloq_click_command

    def _run_command(
        config_file: str,
        output_directory: str,
        overwrite: bool,
        only_config: bool,
        interactive: bool,
        hydra_args: str,
    ) -> None:
        config: DictConfig = load_config(config_file=config_file, hydra_args=hydra_args)
        record = CMDRecord(config=config)
        cmd: Command = cmd_cls(record=record, interactive=interactive)
        record = cmd.run()
        write_record(
            record=record,
            path=output_directory,
            overwrite=overwrite,
            only_config=only_config,
        )

    if use_click:
        _run_command = mloq_click_command(_run_command)
    _run_command.__name__ = cmd_cls.cmd_name
    return _run_command
