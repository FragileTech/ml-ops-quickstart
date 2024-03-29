from pathlib import Path

from omegaconf import DictConfig
import pytest

from mloq.commands.project import (
    code_of_conduct,
    codecov,
    contributing,
    gitignore,
    init,
    main,
    makefile,
    pre_commit_hook,
    ProjectCMD,
    readme,
    test_main,
    test_req,
    version,
)
from mloq.files import File
from mloq.writer import CMDRecord
from tests.test_command import TestCommand


project_conf = {
    "project": dict(
        disable=False,
        project_name="test_project",
        description="test description",
        owner="test_owner",
        license="MIT",
    ),
}

project_conf_with_globals = DictConfig(
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
        "license": {"copyright_holder": "test_holder", "copyright_year": 1990, "license": "MIT"},
        "project": dict(
            disable=False,
            project_name="${globals.project_name}",
            description="${globals.description}",
            owner="${globals.owner}",
            license="${license.license}",
        ),
    },
)
fixture_ids = ["project-conf-cmd", "project-conf-globals"]


@pytest.fixture(
    params=[(ProjectCMD, project_conf), (ProjectCMD, project_conf_with_globals)],
    ids=fixture_ids,
    scope="function",
)
def command_and_config(request):
    command_cls, conf_dict = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, config


def example_files():
    project_path = Path("src") / "test_project"
    module_desc = "Python package header for the project module"
    test_desc = "Python package header for the test module"
    module_init = File(
        name=init.name,
        src=init.src,
        dst=init.dst,
        is_static=init.is_static,
        description=module_desc,
    )
    test_init = File(
        name=init.name,
        src=init.src,
        dst=init.dst,
        is_static=init.is_static,
        description=test_desc,
    )
    example = {
        Path() / makefile.dst: makefile,
        Path() / readme.dst: readme,
        Path() / test_req.dst: test_req,
        Path() / pre_commit_hook.dst: pre_commit_hook,
        Path() / codecov.dst: codecov,
        Path() / gitignore.dst: gitignore,
        Path() / code_of_conduct.dst: code_of_conduct,
        Path() / contributing.dst: contributing,
        project_path / version.dst: version,
        project_path / init.dst: module_init,
        project_path / main.dst: main,
        Path("tests") / test_main.dst: test_main,
        Path("tests") / test_init.dst: test_init,
    }
    return example


cmd_examples_param = [
    (ProjectCMD, project_conf, example_files()),
    (ProjectCMD, project_conf_with_globals, example_files()),
]


@pytest.fixture(params=cmd_examples_param, scope="function", ids=fixture_ids)
def command_and_example(request):
    command_cls, conf_dict, example = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, example
