"""This module contains the functionality for parsing ad modifying the project configuration."""
from pathlib import Path

from ruamel.yaml import load as yaml_load, Loader, YAML as RuamelYAML

from mloq.requirements import require_cuda


def get_docker_python_version(params: dict) -> str:
    """Return the highest python version defined for the project."""
    max_version = list(sorted(params["template"]["python_versions"]))[-1]
    version = max_version.replace(".", "")
    return f"py{version}"


def set_docker_image(params) -> dict:
    """
    Add to params the base docker container that will be used to define the project's container.

    If the dependencies require cuda the base image will be gpu friendly.
    """
    if "base_docker_image" in params["template"]:
        return params
    v = get_docker_python_version(params)
    ubuntu_v = "ubuntu20.04" if v == "py38" else "ubuntu18.04"
    image = (
        f"fragiletech/{ubuntu_v}-cuda-11.0-{v}"
        if require_cuda(params)
        else f"fragiletech/{ubuntu_v}-base-{v}"
    )
    params["template"]["base_docker_image"] = image
    return params


def parse_python_versions(params: dict) -> dict:
    """Add Python 3.8 as a default supported version to the config dictionary."""
    if "python_versions" not in params["template"]:
        params["template"]["python_version"] = ["3.8"]
    # TODO (guillemdb): sanitize input and check for valid python version format
    return params


def read_config(path: Path) -> dict:
    """Load the project configuration from the target path."""
    with open(path, "r") as config:
        params = yaml_load(config.read(), Loader)

    return params


def write_config(config, path):
    """Write config in a yaml file."""
    yaml = RuamelYAML()
    yaml.indent(sequence=4, offset=2)
    with open(path, "w") as f:
        yaml.dump(config, f)
