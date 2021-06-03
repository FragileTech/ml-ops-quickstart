from pathlib import Path

import omegaconf
import pytest

from mloq.files import Ledger


@pytest.fixture(scope="module")
def project_config():
    test_project_config = {
        "open_source": True,
        "docker": True,
        "ci": "python",
        "mlflow": True,
        "docs": False,
        "requirements": ["torch"],
        "git_init": True,
        "git_push": False,
    }
    return test_project_config


@pytest.fixture(scope="module")
def template_config():
    test_template = {
        "project_name": "test_project",
        "default_branch": "master",
        "owner": "owner_test",
        "author": "owner_test",
        "email": "owner@mail.com",
        "copyright_year": 2021,
        "copyright_holder": "owner_test",
        "project_url": "https://github.com/owner_test/test_project",
        "bot_name": "owner_test",
        "bot_email": "owner@mail.com",
        "license": "MIT",
        "description": "test description of the project",
        "python_versions": ["3.6", "3.7", "3.8", "3.9"],
        "docker_image": "fragiletech/ubuntu18.04-cuda-11.0-py39",
        "ci_python_version": "3.8",
        "ci_ubuntu_version": "ubuntu-20.04",
        "ci_extra": "",
        "docstring_checks": False,
        "pyproject_extra": "",
        "git_message": "Test init commit",
    }
    return omegaconf.DictConfig(test_template)


@pytest.fixture(scope="module")
def config(project_config, template_config):
    return omegaconf.DictConfig({"project": project_config, "template": template_config})


@pytest.fixture(scope="module")
def mloq_yaml_dict():
    data = {
        "project": {
            "open_source": True,
            "docker": True,
            "ci": "python",
            "mlflow": False,
            "requirements": ["None"],
            "git_init": True,
            "git_push": False,
        },
        "template": {
            "project_name": "miau",
            "default_branch": "master",
            "owner": "guille",
            "author": "guille",
            "email": "maiol@maic.om",
            "copyright_holder": "guille",
            "project_url": "https://github.com/guille/miau",
            "bot_name": "guille",
            "bot_email": "maiol@maic.om",
            "license": "MIT",
            "description": "caca",
            "python_versions": ["3.6", "3.7", "3.8", "3.9"],
            "docker_image": "fragiletech/ubuntu18.04-base-py39",
            "git_message": "Generate project files with mloq",
        },
    }
    return data


@pytest.fixture()
def repo_path():
    return Path(__file__).parent / "test_project"


@pytest.fixture(scope="function")
def ledger():
    return Ledger()
