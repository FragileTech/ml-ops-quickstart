import os
from pathlib import Path
import tempfile

from omegaconf import DictConfig
import pytest

from mloq.commands.ci import CiCMD
from mloq.files import push_python_wkf
from mloq.runner import run_command
from mloq.test.test_command import TestCommand
from mloq.test.test_runner import dir_trees_are_equal
from mloq.writer import CMDRecord


ci_conf = {
    "ci": dict(
        bot_name="test_bot_name",
        bot_email="test_bot_email",
        disable=False,
        vendor="test_vendor",
        python_versions="3.8",
        ubuntu_version="ubuntu-20.04",
        ci_python_version="3.8",
        ci_ubuntu_version="ubuntu-20.04",
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
    )
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
            python_versions="3.8",
        ),
        "docker": dict(docker_org="test_org"),
        "ci": dict(
            bot_name="test_bot_name",
            bot_email="test_bot_email",
            disable=False,
            vendor="test_vendor",
            python_versions="${package.python_versions}",
            ubuntu_version="ubuntu-20.04",
            ci_python_version="3.8",
            ci_ubuntu_version="ubuntu-20.04",
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
    }
)


@pytest.fixture(params=[ci_conf])
def config1(request):
    return request.param


@pytest.fixture(params=[ci_conf_with_globals])
def config2(request):
    return request.param


@pytest.fixture(params=[(CiCMD, ci_conf), (CiCMD, ci_conf_with_globals)], scope="function")
def command_and_config(request):
    command_cls, conf_dict = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, config


@pytest.fixture()
def example_files():
    return None
    ci_path = Path("ci")
    source_path = ci_path / "source"
    example_files = {
        source_path / push_python_wkf.dst: push_python_wkf,
    }
    return example_files


class TestCi:
    def test_name_is_correct(self, command_and_config):
        command, config = command_and_config
        assert command.name == "ci"

    def _test_file_is_correct(self, example_files, command_and_config):
        source_file = example_files
        source_path = Path("ci") / "source" / push_python_wkf.dst
        target_path = Path(".github") / "workflows" / push_python_wkf.dst
        cmd, config = command_and_config
        cmd.run()
        assert cmd.record.files[target_path] == source_file[Path(source_path)]

    def _test_workflow(self, config1, config2):
        temp_path = tempfile.TemporaryDirectory()
        temp_path1 = Path(temp_path.name) / "target1"
        temp_path2 = Path(temp_path.name) / "target2"
        os.makedirs(temp_path1)
        os.makedirs(temp_path2)
        _run_cmd = run_command(cmd_cls=CiCMD, use_click=False)
        _run_cmd(
            config_file=config1,
            output_directory=temp_path1,
            overwrite=False,
            only_config=False,
            interactive=False,
            hydra_args="",
        )
        _run_cmd(
            config_file=config2,
            output_directory=temp_path2,
            overwrite=False,
            only_config=False,
            interactive=False,
            hydra_args="",
        )
        assert dir_trees_are_equal(str(temp_path1), str(temp_path2))
