import os
from pathlib import Path
import tempfile

from omegaconf import DictConfig, OmegaConf
import pytest

from mloq.commands.license import LicenseCMD
from mloq.files import code_of_conduct, contributing, dco, LICENSES
from mloq.runner import run_command
from mloq.test.test_command import TestCommand  # noqa: F401
from mloq.test.test_runner import dir_trees_are_equal
from mloq.writer import CMDRecord


license_conf = DictConfig(
    {
        "license": dict(
            disable=False,
            license="Apache-2.0",
            copyright_year=1991,
            copyright_holder="test_owner",
            open_source=True,
            project_name="test_name",
            project_url="test_url",
            email="test_email",
        )
    }
)

license_conf_with_globals = DictConfig(
    {
        "globals": {
            "project_name": "test_name",
            "default_branch": "ll",
            "owner": "test_owner",
            "author": "test_author",
            "email": "test_email",
            "description": "supercalifragilisticexpialidocious",
            "open_source": True,
            "project_url": "test_url",
        },
        "license": dict(
            disable=False,
            license="Apache-2.0",
            copyright_year=1991,
            copyright_holder="${globals.owner}",
            open_source="${globals.open_source}",
            project_name="${globals.project_name}",
            project_url="${globals.project_url}",
            email="${globals.email}",
        ),
    }
)

license_non_open_source = DictConfig(
    {
        "globals": {
            "project_name": "test_name",
            "default_branch": "ll",
            "owner": "test_owner",
            "author": "test_author",
            "email": "test_email",
            "description": "supercalifragilisticexpialidocious",
            "open_source": False,
            "project_url": "test_url",
        },
        "license": dict(
            disable=False,
            license="Apache-2.0",  # to test that the license is not added
            copyright_year=1991,
            copyright_holder="${globals.owner}",
            open_source="${globals.open_source}",
            project_name="${globals.project_name}",
            project_url="${globals.project_url}",
            email="${globals.email}",
        ),
    }
)


example_files = {
    Path() / code_of_conduct.dst: code_of_conduct,
    Path() / contributing.dst: contributing,
    Path() / dco.dst: dco,
    Path() / LICENSES[license_conf.license.license].dst: LICENSES[license_conf.license.license],
}

example_files_empty = {}


@pytest.fixture(params=[(license_conf, license_conf_with_globals)])
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


@pytest.fixture(
    params=[
        (LicenseCMD, license_conf),
        (LicenseCMD, license_conf_with_globals),
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
        (LicenseCMD, license_conf, example_files),
        (LicenseCMD, license_conf_with_globals, example_files),
        (LicenseCMD, license_non_open_source, example_files_empty),
    ],
    scope="function",
)
def command_and_example(request):
    command_cls, conf_dict, example = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, example


class TestLicense:
    def test_name_is_correct(self, command_and_config):
        command, config = command_and_config
        assert command.name == "license"

    def test_equivalent_configs(self, config_paths):
        path_conf_1, path_conf_2 = config_paths
        temp_path = tempfile.TemporaryDirectory()
        temp_path1 = Path(temp_path.name) / "target1"
        temp_path2 = Path(temp_path.name) / "target2"
        os.makedirs(temp_path1)
        os.makedirs(temp_path2)
        _run_cmd = run_command(cmd_cls=LicenseCMD, use_click=False)
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
