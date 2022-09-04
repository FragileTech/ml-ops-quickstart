from pathlib import Path

from omegaconf import DictConfig, OmegaConf
import pytest

from mloq.commands.docker import DOCKER_FILES, DockerCMD
from mloq.writer import CMDRecord
from tests.test_command import TestCommand


docker_conf = {
    "docker": dict(
        disable=False,
        project_name="test_project",
        cuda="???",
        cuda_image_type="cudnn8-runtime-ubuntu20.04",
        cuda_version="11.2",
        python_version="3.8",
        ubuntu_version="20.04",
        base_image="???",
        test=True,
        lint=True,
        jupyter=True,
        jupyter_password="test_password",
        docker_org="testorg",
        requirements=[],
        makefile=True,
    ),
}

docker_conf_with_globals = DictConfig(
    {
        "globals": {
            "project_name": "test project",
            "default_branch": "test_branch",
            "owner": "test_owner",
            "author": "test_author",
            "email": "test_email",
            "description": "test_description",
            "open_source": True,
            "project_url": "???",
        },
        "requirements": ["tensorflow"],
        "docker": dict(
            disable=False,
            project_name="${globals.project_name}",
            cuda="???",
            cuda_image_type="cudnn8-runtime-ubuntu20.04",
            cuda_version="11.2",
            python_version="3.8",
            ubuntu_version="20.04",
            base_image="???",
            test=True,
            lint=True,
            jupyter=True,
            jupyter_password="test_password",
            docker_org="testorg",
            requirements="${requirements}",
            makefile=True,
        ),
    },
)


@pytest.fixture(
    params=[(DockerCMD, docker_conf), (DockerCMD, docker_conf_with_globals)],
    scope="function",
)
def command_and_config(request):
    command_cls, conf_dict = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, config


def example_files():

    return {Path() / f.dst: f for f in DOCKER_FILES}


cmd_examples_param = [
    (DockerCMD, docker_conf, example_files()),
    (DockerCMD, docker_conf_with_globals, example_files()),
]


@pytest.fixture(params=cmd_examples_param, scope="function")
def command_and_example(request):
    command_cls, conf_dict, example = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, example


class TestDockerCMD:
    def test_name_is_correct(self, command_and_config):
        command, config = command_and_config
        assert command.cmd_name == "docker"

    def test_parse_cfg_base_image(self, command_and_config):
        command, config = command_and_config

        # assert command.conf.is_missing("base_image"), config.docker
        command.parse_config()
        assert command.base_image is not None
        assert command.record.config.docker.base_image is not None
        assert command.base_image == command.get_base_image()
