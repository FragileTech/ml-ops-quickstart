import pytest

from mloq.parse_config import set_docker_image


supported_versions = ["3.6", "3.7", "3.8"]


@pytest.fixture(params=[supported_versions, supported_versions[:-2], supported_versions[:-1]])
def python_versions(request):
    return request.param


def test_set_docker_image_base(python_versions):
    params = {"template": {"python_versions": python_versions}}
    new_params = set_docker_image(params)
    image_name = new_params["template"]["base_docker_image"]
    if "3.8" in python_versions:
        assert "20.04" in image_name
    else:
        assert "18.04" in image_name
    assert "base" in image_name


def test_set_docker_image_cuda(python_versions):
    params = {"template": {"python_versions": python_versions}, "requirements": ["tf"]}
    new_params = set_docker_image(params)
    image_name = new_params["template"]["base_docker_image"]
    if "3.8" in python_versions:
        assert "20.04" in image_name
    else:
        assert "18.04" in image_name
    assert "cuda" in image_name
