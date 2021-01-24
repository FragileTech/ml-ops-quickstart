"""This module contains the functionality for parsing ad modifying the project configuration."""
from pathlib import Path
from typing import Dict, Optional, Union

from ruamel.yaml import load as yaml_load, Loader, YAML as RuamelYAML

from mloq.config.params import Config
from mloq.files import mloq_yml
from mloq.requirements import require_cuda


def get_docker_python_version(template: dict) -> str:
    """Return the highest python version defined for the project."""
    max_version = list(sorted(template["python_versions"]))[-1]
    version = max_version.replace(".", "")
    return f"py{version}"


def get_docker_image(template: dict, project: dict = None) -> Union[str, None]:
    """
    Add to params the base docker container that will be used to define the project's container.

    If the dependencies require cuda the base image will be gpu friendly.
    """
    project = project or {}
    if "docker_image" in template and template["docker_image"] is not None:
        return template["docker_image"]
    elif project.get("docker") is not None and not project.get("docker"):
        return
    v = get_docker_python_version(template)
    ubuntu_v = "ubuntu20.04" if v == "py38" else "ubuntu18.04"
    image = (
        f"fragiletech/{ubuntu_v}-cuda-11.0-{v}"
        if require_cuda(project)
        else f"fragiletech/{ubuntu_v}-base-{v}"
    )
    return image


def read_config(path: Path) -> dict:
    """Load the project configuration from the target path."""
    with open(path, "r") as config:
        params = yaml_load(config.read(), Loader)

    return params


def read_config_safe(path: Optional[Union[Path, str]]) -> Config:
    """
    Read the configuration file if it exists, otherwise return an empty config dict.

    Args:
        path: If it points to a file, it will read the file and return its content.
              If it points to a directory, it will try to read an mloq.yml file \
              present in that directory.

    Returns:
        Loaded configuration if a config file is present. Empty configuration otherwise.
    """
    if path is None:
        return load_empty_config()
    path = Path(path)
    path = path / mloq_yml.name if path.is_dir() else path
    try:
        return read_config(path)
    except FileNotFoundError:
        return load_empty_config()


def write_config(config, path, safe: bool = False):
    """Write config in a yaml file."""
    yaml = RuamelYAML()
    yaml.indent(sequence=4, offset=2)
    if safe:
        path = Path(path)
        path = path / mloq_yml.name if path.is_dir() else path
    with open(path, "w") as f:
        yaml.dump(config, f)


def load_empty_config() -> Dict[str, Dict[str, None]]:
    """Return a dictionary containing all the MLOQ config values set to None."""
    with open(mloq_yml.src, "r") as config:
        empty_config = yaml_load(config.read(), Loader)
    return empty_config
