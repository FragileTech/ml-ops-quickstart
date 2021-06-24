from pathlib import Path
from typing import NamedTuple, Tuple

from omegaconf import DictConfig

from mloq.failure import MissingConfigValue
from mloq.writer import CMDRecord


class Command:
    name = ""
    files = tuple()
    CONFIG: NamedTuple = NamedTuple("Config", [])()

    def __init__(self, record: CMDRecord, interactive: bool = False):
        self._record = record
        self.interactive = interactive

    @property
    def record(self) -> CMDRecord:
        return self._record

    @property
    def directories(self) -> Tuple[Path]:
        return tuple()

    def parse_config(self) -> DictConfig:
        config = getattr(self.record.config, self.name)  # TODO: gestionar caso de config vacio.
        for param in self.CONFIG:
            try:
                value = param(config, self.interactive)
            except MissingConfigValue as e:
                msg = f"Config value {param.name} not defined for {self.name} command."
                raise MissingConfigValue(msg) from e

            setattr(config, param.name, value)
        return self.record.config

    def interactive_config(self) -> DictConfig:
        return self.parse_config()

    def record_files(self) -> None:
        if len(self.files) > 0:
            raise NotImplementedError

    def record_directories(self) -> None:
        for directory in self.directories:
            self._record.register_directory(directory)

    def configure(self) -> None:
        if self.interactive:
            config = self.interactive_config()
        else:
            config = self.parse_config()
        self.record.update_config(config)

    def run_side_effects(self) -> None:
        pass

    def run(self) -> CMDRecord:
        self.configure()
        self.record_directories()
        self.record_files()
        self.run_side_effects()
        return self.record
