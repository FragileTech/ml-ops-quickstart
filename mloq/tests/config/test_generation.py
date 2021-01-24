import copy
import os

import pytest

from mloq.config.generation import generate_project_config, generate_template


@pytest.fixture()
def project_config():
    test_project_config = {
        "open_source": True,
        "proprietary": False,
        "docker": True,
        "ci": "python",
        "mlflow": True,
        "requirements": ["torch"],
    }
    return test_project_config


@pytest.fixture()
def template():
    test_template = {
        "project_name": "test_project",
        "default_branch": "master",
        "owner": "owner_test",
        "author": "owner_test",
        "email": "owner@mail.com",
        "copyright_holder": "owner_test",
        "project_url": "https://github.com/owner_test/test_project",
        "bot_name": "owner_test",
        "bot_email": "owner@mail.com",
        "license": "MIT",
        "description": "test description of the project",
        "python_versions": ["3.6", "3.7", "3.8", "3.9"],
        "docker_image": "fragiletech/ubuntu18.04-cuda-11.0-py39",
    }
    return test_template


def compare_dicts(a, b):
    for (k1, v1), (k2, v2) in zip(a.items(), b.items()):
        assert k1 == k2
        if not isinstance(v1, list):
            assert v1 == v2
        else:
            for x1, x2 in zip(v1, v2):
                assert x1 == x2


def test_generate_config(project_config):
    in_config = copy.deepcopy(project_config)
    in_config["requirements"] = None
    os.environ["MLOQ_REQUIREMENTS"] = "torch"
    new_template = generate_project_config(project_config=in_config, interactive=False)
    del os.environ["MLOQ_REQUIREMENTS"]
    compare_dicts(project_config, new_template)


def test_generate_template(template):
    in_template = copy.deepcopy(template)
    in_template["project_name"] = None
    os.environ["MLOQ_PROJECT_NAME"] = "test_project"
    new_template = generate_template(template=in_template, interactive=False)
    del os.environ["MLOQ_PROJECT_NAME"]
    compare_dicts(template, new_template)
