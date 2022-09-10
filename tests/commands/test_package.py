import os
from pathlib import Path
import tempfile

from omegaconf import DictConfig, OmegaConf
import pytest

from mloq.commands.package import PackageCMD, pyproject_toml, setup_py
from mloq.runner import run_command
from mloq.writer import CMDRecord
from tests import TestCommand  # noqa: F401
from tests.test_runner import dir_trees_are_equal


package_conf = DictConfig(
    {
        "package": dict(
            disable=False,
            project_name="test_package",
            description="configuration for package tests",
            default_branch="test_branch_package",
            project_url="test_url",
            owner="test_owner",
            author="test_author",
            email="test_email",
            license="MIT",
            python_versions=["3.6", "3.7", "3.8", "3.9"],
            pyproject_extra="",
            license_classifier="???",
        ),
        "lint": dict(project_name="${package.project_name}"),
    }
)

package_conf_with_globals = DictConfig(
    {
        "globals": {
            "project_name": "test_package",
            "default_branch": "test_branch_package",
            "owner": "test_owner",
            "author": "test_author",
            "email": "test_email",
            "description": "configuration for package tests",
            "open_source": True,
            "project_url": "test_url",
        },
        "license": dict(
            license="MIT",
        ),
        "package": dict(
            disable=False,
            project_name="${globals.project_name}",
            description="${globals.description}",
            default_branch="${globals.default_branch}",
            project_url="${globals.project_url}",
            owner="${globals.owner}",
            author="${globals.author}",
            email="${globals.email}",
            license="${license.license}",
            python_versions=["3.6", "3.7", "3.8", "3.9"],
            pyproject_extra="",
            license_classifier="???",
        ),
        "lint": dict(
            project_name="${globals.project_name}",
        ),
    }
)


example_files = {
    Path() / pyproject_toml.dst: pyproject_toml,
    Path() / setup_py.dst: setup_py,
}


@pytest.fixture(params=[(package_conf, package_conf_with_globals)])
def config_paths(request):
    c1, c2 = request.param
    temp_path = tempfile.TemporaryDirectory()
    conf_1 = DictConfig(c1)
    conf_2 = DictConfig(c2)
    filepath_1 = Path(temp_path.name) / "mloq1.yaml"
    filepath_2 = Path(temp_path.name) / "mloq2.yaml"
    with open(filepath_1, "w") as f:
        OmegaConf.save(conf_1, f)
    with open(filepath_2, "w") as f:
        OmegaConf.save(conf_2, f)
    yield filepath_1, filepath_2
    temp_path.cleanup()


@pytest.fixture(
    params=[
        (PackageCMD, package_conf),
        (PackageCMD, package_conf_with_globals),
    ],
    scope="function",
)
def command_and_config(request):
    command_cls, conf_dict = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, config


@pytest.fixture(
    params=[
        (PackageCMD, package_conf, example_files),
        (PackageCMD, package_conf_with_globals, example_files),
    ],
    scope="function",
)
def command_and_example(request):
    command_cls, conf_dict, example = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, example


class TestPackage:
    def test_name_is_correct(self, command_and_config):
        command, config = command_and_config
        assert command.cmd_name == "package"

    def test_equivalent_configs(self, config_paths):
        path_conf_1, path_conf_2 = config_paths
        temp_path = tempfile.TemporaryDirectory()
        temp_path1 = Path(temp_path.name) / "target1"
        temp_path2 = Path(temp_path.name) / "target2"
        os.makedirs(temp_path1)
        os.makedirs(temp_path2)
        _run_cmd = run_command(cmd_cls=PackageCMD, use_click=False)
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
