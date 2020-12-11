from pathlib import Path

from ruamel.yaml import load as yaml_load, Loader

from mloq.requirements_config import require_cuda


def get_docker_python_version(params) -> str:
    max_version = list(sorted(params["template"]["python_versions"]))[-1]
    version = max_version.replace(".", "")
    return f"py{version}"


def set_docker_image(params) -> dict:
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
    if "python_versions" not in params["template"]:
        params["template"]["python_version"] = ["3.8"]
    # TODO (guillemdb): sanitize input and check for valid python version format
    return params


def read_config(path: Path) -> dict:
    with open(path, "r") as config:
        params = yaml_load(config.read(), Loader)
    params = parse_python_versions(params)
    params = set_docker_image(params)
    return params
