"""This module defines all the different assets accessible from mloq."""
from pathlib import Path
import sys
from typing import NamedTuple, Optional, Union


class File(NamedTuple):
    """
    Generates project files.

    This class defines templating files, which will be rendered according
    to the user's configuration. Besides, File instances have additional
    attributes used for specifying the destination of the generated file.

    Attributes of this class:
        name: Name of the templating file.
        src: Location of the templating file.
        dst: Name of the file generated from the templating file.
        description: Short description of the current file.
        is_static: Boolean value. If True, the templating file does not
            admit render parameters.
    """

    name: str
    src: Path
    dst: Path
    description: str
    is_static: bool


def file(
    name: str,
    path: Union[Path, str],
    description: Optional[str] = None,
    dst: Optional[Union[Path, str]] = None,
    is_static: bool = False,
) -> File:
    """Define a new asset as a File namedtuple."""
    if description is None:
        print("FIXME: %s must have a description" % name, file=sys.stderr)
        description = "TODO"
    dst = Path(dst) if dst is not None else name
    return File(
        name=name,
        src=Path(path) / name,
        dst=dst,
        description=description,
        is_static=is_static,
    )


# Assets paths
ASSETS_PATH = Path(__file__).parent / "assets"
SHARED_ASSETS_PATH = ASSETS_PATH / "shared"
MLOQ_ASSETS_PATH = ASSETS_PATH / "mloq"
REQUIREMENTS_PATH = ASSETS_PATH / "requirements"

# Mloq files
mloq_yml = file(
    "mloq.yaml",
    MLOQ_ASSETS_PATH,
    "mloq configuration, you can safely remove it if you don't plan to upgrade",
    is_static=True,
)
what_mloq_generated = file("WHAT_MLOQ_GENERATED.md", MLOQ_ASSETS_PATH, "this file")
# Requirements files

requirements = file(
    "requirements.txt",
    REQUIREMENTS_PATH,
    "list of exact versions of the packages on which your project depends",
    is_static=True,
)

dogfood_req = file(
    "dogfood.txt",
    REQUIREMENTS_PATH,
    "list of mock requirements for testing purposes",
    is_static=True,
)

# Shared templates
makefile = file("Makefile", SHARED_ASSETS_PATH, "common make commands for development")

pyproject_toml = file(
    "pyproject.toml",
    SHARED_ASSETS_PATH,
    "configuration of various development tools: linters, formatters, packaging",
)


def read_file(file: File) -> str:
    """Return and string with the content of the provided file."""
    with open(file.src, "r") as f:
        return f.read()
