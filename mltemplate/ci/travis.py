import ruamel.yaml

from mltemplate.ci.commands import (
    install_python_project,
    coverage_script,
    style_script,
    style_install,
    docker_test_script,
    dockerhub_install,
    dockerhub_script,
    dockerhub_deploy_script,
    bump_version_script,
    bump_version_install,
    pypi_install,
    pypi_deploy_script,
    pypi_script,
)

style_stage = {
    "stage": "style",
    "if": "commit_message !~ /^Bump version/",
    "name": "Check code style",
    "python": 3.8,
    "script": style_script,
    "install": style_install,
}

docker_test_stage = {
    "stage": "test",
    "if": "commit_message !~ /^Bump version/",
    "name": "Tests inside docker",
    "script": docker_test_script,
}

bump_version_stage = {
    "stage": "bump-version",
    "if": "branch == master AND type != pull_request AND commit_message !~ /^Bump version/",
    "name": "Bump the version",
    "install": bump_version_install,
    "script": bump_version_script,
}

pypi_stage = {
    "stage": "deploy",
    "if": "tag =~ .*",
    "name": "Push package to PyPI",
    "install": pypi_install,
    "script": pypi_script,
    "deploy": {
        "provider": "script",
        "script": pypi_deploy_script,
        "skip_cleanup": True,
        "on": {"tags": True},
    },
}

dockerhub_stage = {
    "stage": "deploy",
    "if": "tag =~ .*",
    "name": "Push docker image to DockerHub",
    "install": dockerhub_install,
    "script": dockerhub_script,
    "deploy": {
        "provider": "script",
        "script": dockerhub_deploy_script,
        "skip_cleanup": True,
        "on": {"tags": True},
    },
}


def create_config_dict(
    stages, install_script=install_python_project, coverage_script=coverage_script
):
    matrix = {
        "fast_finish": True,
        "include": stages,
    }

    common_travis = {
        "language": "python",
        "sudo": True,
        "dist": "bionic",
        "services": ["docker"],
        "cache": "pip",
        "&_install&": install_script,
        "&_coverage&": coverage_script,
        "before_cache": ["chown -R travis:travis $HOME/.cache/pip"],
        "stages": [],
        "before_install": ["env"],
        "matrix": matrix,
        "notifications": {"email": False},
    }
    return common_travis


def create_test_stage(python_version, run_coverage: bool = False):
    stage = {
        "stage": "test",
        "if": "commit_message !~ /^Bump version/",
        "name": f"Test python {python_version}",
        "python": python_version,
        "script": "*`_coverage`*",
        "install": "*`_install`*",
    }
    if run_coverage:
        stage["after_success"] = ["codecov"]
    return stage


stage_names = ("style", "python_test", "docker_test", "bump_version", "pypi", "dockerhub")
stages_dict = {
    "style": style_stage,
    "docker_test": docker_test_stage,
    "bump_version": bump_version_stage,
    "pypi": pypi_stage,
    "dockerhub": dockerhub_stage,
}


def create_stages_config(stage_names=stage_names, python_versions=None):
    python_versions = python_versions if python_versions is not None else (3.6, 3.7, 3.8)
    stages = []
    for name in stage_names:
        if name == "python_test":
            stages = stages + [create_test_stage(v) for v in python_versions]
        else:
            stages.append(stages_dict[name])
    return stages


def create_travis_ci_config(stage_names=stage_names, python_versions=None):
    stages = create_stages_config(stage_names, python_versions)
    data = create_config_dict(stages)
    return data


def format_output_yaml(params):
    def clean_yaml(s):
        s = format_aliases(s)
        s = fill_in_template(params, s)
        return s

    return clean_yaml


def export_travis_config(path, params, stage_names, python_versions):
    yaml = ruamel.yaml.YAML()
    yaml.indent(sequence=4, offset=2)
    with open(path / ".travis.yml", "w") as f:
        config = create_travis_ci_config(stage_names, python_versions)
        yaml.dump(config, f, transform=format_output_yaml(params))
