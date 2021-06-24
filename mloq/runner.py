from pathlib import Path
import sys
from typing import Callable
from unittest.mock import patch

import hydra
from omegaconf import DictConfig, OmegaConf

from mloq import _logger
from mloq.command import Command
from mloq.files import mloq_yml
from mloq.record import CMDRecord
from mloq.writer import Writer


def load_config(config_file, hydra_args) -> DictConfig:
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

        @hydra.main(config_name=config_file.name)
        def load_config(loaded_config: DictConfig):
            nonlocal config
            config = loaded_config

        with patch("sys.argv", [sys.argv[0]] + list(hydra_args)):
            load_config()
    else:
        _logger.info("No mloq.yml file provided. Creating a new configuration")
        config = OmegaConf.load(mloq_yml.src)
    return config


def write_record(record, path, overwrite: bool = False, only_config: bool = False) -> None:
    if only_config:
        with open(Path(path) / mloq_yml.dst, "w") as f:
            OmegaConf.save(config=record.config, f=f)
    else:
        writer = Writer(record=record, overwrite=overwrite, path=path)
        writer.run()


def run_command(cmd_cls, use_click: bool = True) -> Callable:
    from mloq.cli import mloq_command

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
        _run_command = mloq_command(_run_command)
    _run_command.__name__ = cmd_cls.name
    return _run_command
