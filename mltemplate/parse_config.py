from ruamel.yaml import Loader, load as yaml_load


def get_docker_image(params):
    # Todo: parse python version from params
    if "torch" in params["requirements"] or "tensorflow" in params["requirements"]:
        params["template"]["base_docker_image"] = "fragiletech/ubuntu20.04-cuda-11.0-py38"
    else:
        params["template"]["base_docker_image"] = "fragiletech/ubuntu20.04-base-py38"
    return params


def parse_config(path):
    with open(path, "r") as config:
        params = yaml_load(config.read(), Loader)
    params = get_docker_image(params)
    return params
