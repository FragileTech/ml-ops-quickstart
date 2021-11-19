import os
from pathlib import Path
import tempfile

from omegaconf import DictConfig, OmegaConf
import pytest

from mloq.commands.ci import CiCMD
from mloq.files import push_python_wkf
from mloq.runner import run_command
from mloq.writer import CMDRecord
from tests import TestCommand  # noqa: F401
from tests.test_runner import dir_trees_are_equal


ci_conf = {
    "ci": dict(
        bot_name="test_bot_name",
        bot_email="test_bot_email",
        disable=False,
        vendor="test_vendor",
        python_versions=["3.8"],
        # ci_ubuntu_version="ubuntu-20.04",
        ci_python_version="3.8",
        ubuntu_version="ubuntu-20.04",
        ci_extra="",
        open_source=True,
        project_name="test_name",
        default_branch="test_branch",
        owner="test_owner",
        author="test_author",
        email="test_email",
        project_url="test_url",
        docker=True,
        docker_org="test_org",
    ),
}

ci_conf_with_globals = DictConfig(
    {
        "globals": {
            "project_name": "test_name",
            "default_branch": "test_branch",
            "owner": "test_owner",
            "author": "test_author",
            "email": "test_email",
            "description": "test_description",
            "open_source": True,
            "project_url": "test_url",
        },
        "package": dict(
            python_versions=["3.8"],
            disable=False,
        ),
        "docker": dict(docker_org="test_org", disable=False),
        "ci": dict(
            bot_name="test_bot_name",
            bot_email="test_bot_email",
            disable=False,
            vendor="test_vendor",
            python_versions="${package.python_versions}",
            ubuntu_version="ubuntu-20.04",
            ci_python_version="3.8",
            # ci_ubuntu_version="ubuntu-20.04",
            ci_extra="",
            open_source="${globals.open_source}",
            project_name="${globals.project_name}",
            default_branch="${globals.default_branch}",
            owner="${globals.owner}",
            author="${globals.author}",
            email="${globals.email}",
            project_url="${globals.project_url}",
            docker=True,
            docker_org="${docker.docker_org}",
        ),
    },
)


@pytest.fixture(params=[(ci_conf, ci_conf_with_globals)])
def config_paths(request):
    c1, c2 = request.param
    temp_path = tempfile.TemporaryDirectory()
    conf_1 = DictConfig(c1)
    conf_2 = DictConfig(c2)
    filepath_1 = Path(temp_path.name) / "mloq1.yml"
    filepath_2 = Path(temp_path.name) / "mloq2.yml"
    with open(filepath_1, "w") as f:
        OmegaConf.save(conf_1, f)
    with open(filepath_2, "w") as f:
        OmegaConf.save(conf_2, f)
    yield filepath_1, filepath_2
    temp_path.cleanup()


@pytest.fixture(params=[(CiCMD, ci_conf), (CiCMD, ci_conf_with_globals)], scope="function")
def command_and_config(request):
    command_cls, conf_dict = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, config


example_files = {
    Path(".github") / "workflows" / push_python_wkf.dst: push_python_wkf,
}


@pytest.fixture(
    params=[(CiCMD, ci_conf, example_files), (CiCMD, ci_conf_with_globals, example_files)],
    scope="function",
)
def command_and_example(request):
    command_cls, conf_dict, example = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, example


class TestCi:
    def test_name_is_correct(self, command_and_config):
        command, config = command_and_config
        assert command.cmd_name == "ci"

    def test_equivalent_configs(self, config_paths):
        path_conf_1, path_conf_2 = config_paths
        temp_path = tempfile.TemporaryDirectory()
        temp_path1 = Path(temp_path.name) / "target1"
        temp_path2 = Path(temp_path.name) / "target2"
        os.makedirs(temp_path1)
        os.makedirs(temp_path2)
        _run_cmd = run_command(cmd_cls=CiCMD, use_click=False)
        _run_cmd(
            config_file=path_conf_1,
            output_directory=temp_path1,
            overwrite=False,
            only_config=False,
            interactive=False,
            hydra_args="",
        )
        _run_cmd(
            config_file=path_conf_2,
            output_directory=temp_path2,
            overwrite=False,
            only_config=False,
            interactive=False,
            hydra_args="",
        )
        assert dir_trees_are_equal(str(temp_path1), str(temp_path2))
        temp_path.cleanup()
