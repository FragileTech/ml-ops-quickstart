"""This module contains the functionality for parsing ad modifying the project configuration."""
from pathlib import Path
from typing import Union

from omegaconf import DictConfig, OmegaConf

from mloq.files import docs_yml, setup_yml
from mloq.requirements import require_cuda


def get_docker_python_version(template: DictConfig) -> str:
    """Return the highest python version defined for the project."""
    max_version = list(sorted(template["python_versions"]))[-1]
    version = max_version.replace(".", "")
    return f"py{version}"


def get_docker_image(config: DictConfig) -> Union[str, None]:
    """
    Add to params the base docker container that will be used to define the project's container.

    If the dependencies require cuda the base image will be gpu friendly.
    """
    docker_is_false = not config.project.get("docker")
    if docker_is_false:  # Project does not require Docker
        return "empty"
    # If docker image is defined, return current value even if it's an empty image
    if config.template.get("docker_image") is not None:
        return config.template["docker_image"]
    # Define the appropriate FragileTech docker container as base image
    v = get_docker_python_version(config.template)
    ubuntu_v = "ubuntu20.04" if v == "py38" else "ubuntu18.04"
    image = (
        f"fragiletech/{ubuntu_v}-cuda-11.0-{v}"
        if require_cuda(config.project)
        else f"fragiletech/{ubuntu_v}-base-{v}"
    )
    return image


def write_config_setup(config: DictConfig, path: Union[Path, str], safe: bool = False):
    """Write setup config in a yaml file."""
    if safe:
        path = Path(path)
        path = path / setup_yml.dst if path.is_dir() else path
    with open(path, "w") as f:
        OmegaConf.save(config, f)


def load_empty_config_setup() -> DictConfig:
    """Return a dictionary containing all the MLOQ setup config values set to None."""
    return OmegaConf.load(setup_yml.src)


def write_config_docs(config: DictConfig, path: Union[Path, str], safe: bool = False):
    """Write docs config in a yaml file."""
    if safe:
        path = Path(path)
        path = path / docs_yml.dst if path.is_dir() else path
    with open(path, "w") as f:
        OmegaConf.save(config, f)


def load_empty_config_docs() -> DictConfig:
    """Return a dictionary containing all the MLOQ docs config values set to None."""
    return OmegaConf.load(docs_yml.src)
