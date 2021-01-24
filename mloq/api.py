"""The api module exposes the mloq functionality to the CLI."""
import copy
from pathlib import Path
from typing import Union

from mloq.config import Config
from mloq.directories import create_project_directories
from mloq.files import mlproject, OPEN_SOURCE_FILES, ROOT_PATH_FILES, SCRIPTS, setup_py, test_main
from mloq.requirements import setup_requirements
from mloq.templating import write_template
from mloq.workflows import setup_push_workflow


def requirements(
    project_config: Config,
    path: Union[Path, str],
    lint: bool = True,
    test: bool = True,
    install=None,
    override: bool = False,
):
    """Write requirements files and install them if requested."""
    if isinstance(install, (tuple, list)) and "all" in install or install == "all":
        install_reqs = True
        install_lint = True
        install_test = True
    elif isinstance(install, (tuple, list)):
        install_reqs = "reqs" in install or "requirements" in install
        install_lint = "lint" in install
        install_test = "test" in install
    else:
        install_reqs = False
        install_lint = False
        install_test = False
    options = project_config.get("requirements", ["empty"])
    setup_requirements(
        options=options,
        path=Path(path),
        test=test,
        lint=lint,
        install_test=install_test,
        install_reqs=install_reqs,
        install_lint=install_lint,
        override=override,
    )


def setup_project_files(path, template: Config, project_config: Config, override: bool = False):
    """Write the template for common repository config files."""
    path = Path(path)
    _template = copy.deepcopy(template)
    _template["project_name"] = _template["project_name"].replace("-", "_")
    project_name = _template["project_name"]
    create_project_directories(project_name=project_name, root_path=path, override=override)
    setup_root_files(
        template=_template, project_config=project_config, path=path, override=override
    )
    tests_path = path / project_name / "tests"
    write_template(test_main, template=_template, path=tests_path, override=override)


def setup_scripts(path: Union[str, Path], template: Config, override: bool = False):
    """Initialize CI scripts folder files."""
    path = Path(path)
    path = path if path.name == "scripts" else path / "scripts"
    for file in SCRIPTS:
        write_template(file, template=template, path=path, override=override)


def setup_root_files(
    path: Union[str, Path], template: Config, project_config: Config, override: bool = False
):
    """Initialize root folder files."""
    for file in ROOT_PATH_FILES:
        write_template(file, template=template, path=path, override=override)
    if project_config.get("mlflow"):
        write_template(mlproject, template=template, path=path, override=override)
    if project_config.get("open_source"):
        for file in OPEN_SOURCE_FILES:
            write_template(file, template=template, path=path, override=override)
    propietary_classif = "License :: Other/Proprietary License"
    license_classifiers = {"mit": "License :: OSI Approved :: MIT License"}
    setup_template = copy.deepcopy(template)
    license_classif = license_classifiers.get(template["license"], propietary_classif)
    setup_template["license_classifier"] = license_classif
    write_template(setup_py, template=setup_template, path=path, override=override)


def setup_repository(
    path: Union[str, Path], template: Config, project_config: Config, override: bool = False,
):
    """Initialize the project folder structure and all the filled in boilerplate files."""
    path = Path(path)
    setup_project_files(
        path=path, template=template, project_config=project_config, override=override
    )
    setup_push_workflow(
        project_config=project_config, path=path, template=template, override=override
    )
    requirements(project_config=project_config, path=path, test=True, lint=True, override=override)
    setup_scripts(template=template, path=path, override=override)
