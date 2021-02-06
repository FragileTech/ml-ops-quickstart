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
        "ci_python_version": "3.8",
        "ci_ubuntu_version": "ubuntu-20.04",
        "ci_extra_setup": "",
        "git_message": "Test init commit",
    }
    return test_template


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
