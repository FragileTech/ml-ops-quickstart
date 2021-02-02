import pytest


@pytest.fixture(scope="module")
def project_config():
    test_project_config = {
        "open_source": True,
        "docker": True,
        "ci": "python",
        "mlflow": True,
        "requirements": ["torch"],
        "git_init": True,
        "git_push": False,
    }
    return test_project_config


@pytest.fixture(scope="module")
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
        "git_message": "Test init commit",
    }
    return test_template
