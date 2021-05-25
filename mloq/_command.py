from pathlib import Path
import sys
from typing import Union
from unittest.mock import patch

import hydra
from omegaconf import DictConfig


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


class Command:

    def __init__(
        self,
        config: DictConfig,
        output_directory: Union[Path, str],
        overwrite: bool,
        interactive: bool,
        only_config: bool,
        ledger: "Ledger",
    ):

        self._config = config
        self._output_directory = Path(output_directory)
        self._overwrite = overwrite
        self._interactive = interactive
        self._only_config = only_config
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

    def __call__(self, ledger=None):
        self.ledger = Ledger() if ledger is None else self.ledger
        if not isinstance(self.ledger, Ledger):
            raise ValueError("Please specify a Ledger")
        return self.run()

    def create_directories(self) -> None:
        raise NotImplementedError

    def write_templates(self) -> None:
        raise NotImplementedError

    def generate_config(self) -> DictConfig:
        raise NotImplementedError

    def interactive_config(self) -> DictConfig:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError
