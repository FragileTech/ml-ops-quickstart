"""This module defines common functionality for dealing with project requirements."""
import os
from pathlib import Path
from typing import Iterable

from mloq.directories import copy_file
from mloq.files import (
    data_science_req,
    data_viz_req,
    File,
    lint_req,
    pytorch_req,
    tensorflow_req,
    test_req,
)


REQUIREMENTS_ALIASES = {
    data_science_req: ["data-science", "datascience", "ds"],
    pytorch_req: ["pytorch", "torch"],
    tensorflow_req: ["tensorflow", "tf"],
    data_viz_req: ["data-visualization", "data-viz", "data-vis", "dataviz", "datavis"],
}


def require_cuda(template: dict) -> bool:
    """Return True if any of the project dependencies require CUDA."""
    if "requirements" not in template:
        return False
    options = template["requirements"]
    tf_alias = REQUIREMENTS_ALIASES[tensorflow_req]
    torch_alias = REQUIREMENTS_ALIASES[pytorch_req]
    for option in options:
        if option in tf_alias or option in torch_alias:
            return True
    return False


def get_aliased_requirements_file(option: str) -> File:
    """Get requirement file from aliased name."""
    for file, valid_alias in REQUIREMENTS_ALIASES.items():
        if option in valid_alias:
            return file
    raise KeyError(f"{option} is not a valid name. Valid aliases are {REQUIREMENTS_ALIASES}")


def read_requirements_file(option: str) -> str:
    """Return the content of the target requirements file form an aliased name."""
    req_file = get_aliased_requirements_file(option)
    with open(req_file.src, "r") as f:
        return f.read()


def compose_requirements(options: Iterable[str]) -> str:
    """
    Return the content requirements.txt file with pinned dependencies.

    The returned string contains the combined dependencies\
     for the different options sorted alphabetically.

    Args:
        options: Iterable containing the aliased names of the target dependencies for the project.

    Returns:
        str containing the pinned versions of all the selected requirements.
    """
    requirements_text = ""
    for i, opt in enumerate(options):
        pref = "\n" if i > 0 else ""  # Ensure one requirement per line
        requirements_text += pref + read_requirements_file(opt)
    # Sort requirements alphabetically
    requirements_text = "\n".join(sorted(requirements_text.split("\n"))).lstrip("\n")
    return requirements_text


def write_requirements(
    options, out_path=None, out_name="requirements.txt", override: bool = False
):
    """
    Write the composed requirements.txt file.

    The writen file contains pinned dependencies for the libraries \
    required by the provided options.
    """
    out_path = os.getcwd() if out_path is None else out_path
    file_path = out_path / out_name
    if not override and file_path.exists():
        return
    requirements = compose_requirements(options) if options is not None else ""
    with open(file_path, "w") as f:
        f.write(requirements)


def write_dev_requirements(out_path=None, override: bool = False):
    """Write requirements-lint.txt and requirements-test.txt in the target directory."""
    out_path = Path(os.getcwd() if out_path is None else out_path)
    copy_file(lint_req, out_path, override)
    copy_file(test_req, out_path, override)


def setup_requirements(
    options=None, out_path=None, out_name="requirements.txt", override: bool = False
):
    """Write the different requirements.txt files for the project."""
    out_path = Path(os.getcwd() if out_path is None else out_path)
    if options is not None:
        write_requirements(
            options=options, out_path=out_path, out_name=out_name, override=override
        )
    write_dev_requirements(out_path, override=override)
