"""config contains all the logic needed to define the configuration of a new mloq project."""
from typing import Any, Dict, List, Set, Tuple, Union


Config = Dict[str, Union[None, str, Dict[str, Any], List[str]]]
Choices = Union[List[str], Tuple[str], Set[str]]
