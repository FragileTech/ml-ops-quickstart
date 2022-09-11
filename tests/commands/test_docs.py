from pathlib import Path

from omegaconf import DictConfig
import pytest

from mloq.commands.docs import (
    conf_py,
    deploy_docs,
    docs_req,
    DocsCMD,
    index_md,
    make_bat_docs,
    makefile_docs,
)
from mloq.writer import CMDRecord


docs_conf = {
    "docs": dict(
        disable=False,
        deploy_docs=True,
        project_name="test_project",
        description="test description",
        author="test_author",
        copyright_holder="test_copyright_holder",
        copyright_year="1990",
        default_branch="test_branch",
    ),
}

docs_conf_with_globals = DictConfig(
    {
        "globals": {
            "project_name": "test_name",
            "default_branch": "test_branch",
            "owner": "test_owner",
            "author": "test_author",
            "email": "test_email",
            "description": "test_description",
            "open_source": True,
            "project_url": "???",
        },
        "license": {"copyright_holder": "test_holder", "copyright_year": 1990},
        "docs": dict(
            disable=False,
            deploy_docs=True,
            project_name="${globals.project_name}",
            description="${globals.description}",
            author="${globals.author}",
            copyright_holder="${license.copyright_holder}",
            copyright_year="${license.copyright_year}",
        ),
    },
)

fixture_ids = ["docs-conf-cmd", "docs-conf-globals"]


@pytest.fixture(
    params=[(DocsCMD, docs_conf), (DocsCMD, docs_conf_with_globals)],
    scope="function",
    ids=fixture_ids,
)
def command_and_config(request):
    command_cls, conf_dict = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, config


def example_files(deploy_docs=True):
    docs_path = Path("docs")
    source_path = docs_path / "source"
    example = {
        source_path / conf_py.dst: conf_py,
        source_path / index_md.dst: index_md,
        docs_path / makefile_docs.dst: makefile_docs,
        docs_path / make_bat_docs.dst: make_bat_docs,
        docs_path / docs_req.dst: docs_req,
    }
    if deploy_docs:
        example[Path(".github") / "workflows"] = deploy_docs
    return example


cmd_examples_param = [
    (DocsCMD, docs_conf, example_files()),
    (DocsCMD, docs_conf_with_globals, example_files()),
]


@pytest.fixture(params=cmd_examples_param, scope="function", ids=fixture_ids)
def command_and_example(request):
    command_cls, conf_dict, example = request.param
    config = DictConfig(conf_dict)
    record = CMDRecord(config)
    command = command_cls(record=record)
    return command, example


class TestDocs:
    def test_name_is_correct(self, command_and_config):
        command, config = command_and_config
        assert command.cmd_name == "docs"
