"""config contains all the logic needed to define the configuration of a new mloq project."""
from typing import List, Set, Tuple, Union

from omegaconf import DictConfig


Config = DictConfig
Choices = Union[List[str], Tuple[str], Set[str]]
