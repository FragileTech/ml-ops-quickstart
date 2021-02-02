"""The api module exposes the mloq functionality to the CLI."""
import copy
from pathlib import Path
from typing import List, Tuple, Union

from mloq.config import Config
from mloq.directories import create_project_directories
from mloq.files import mlproject, OPEN_SOURCE_FILES, ROOT_PATH_FILES, SCRIPTS, setup_py, test_main
from mloq.git import setup_git
from mloq.requirements import install_requirements, write_requirements
from mloq.templating import write_template
from mloq.workflows import setup_push_workflow


def setup_requirements(
    path: Union[Path, str],
    project_config: Config,
    lint: bool = True,
    test: bool = True,
    install: Union[str, Tuple[str], List[str], None] = None,
    override: bool = False,
) -> None:
    """Write requirements files and install them if requested."""
    if isinstance(install, (tuple, list)) and "all" in install or install == "all":
        install_reqs = install_lint = install_test = True
    elif isinstance(install, (tuple, list)):
        install_reqs = "reqs" in install or "requirements" in install
        install_lint = "lint" in install
        install_test = "test" in install
    else:
        install_reqs = install_lint = install_test = False
    options = project_config.get("requirements", ["empty"])
    write_requirements(
        out_path=path,
        options=options,
        test=test,
        lint=lint,
        override=override,
    )
    install_requirements(
        path=path,
        requirements=install_reqs,
        test=install_test,
        lint=install_lint,
        py3=True,
    )


def setup_project_files(
    path: Union[Path, str],
    template: Config,
    project_config: Config,
    override: bool = False,
) -> None:
    """Write the template for common repository config files."""
    path = Path(path)
    _template = copy.deepcopy(template)
    _template["project_name"] = _template["project_name"].replace("-", "_")
    project_name = _template["project_name"]
    create_project_directories(project_name=project_name, root_path=path, override=override)
    setup_root_files(
        template=_template,
        project_config=project_config,
        path=path,
        override=override,
    )
    tests_path = path / project_name / "tests"
    write_template(test_main, template=_template, path=tests_path, override=override)


def setup_scripts(path: Union[str, Path], template: Config, override: bool = False) -> None:
    """Initialize CI scripts folder files."""
    path = Path(path)
    path = path if path.name == "scripts" else path / "scripts"
    for file in SCRIPTS:
        write_template(file, template=template, path=path, override=override)


def setup_root_files(
    path: Union[str, Path],
    template: Config,
    project_config: Config,
    override: bool = False,
) -> None:
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


def setup_project(
    path: Union[str, Path],
    template: Config,
    project_config: Config,
    override: bool = False,
) -> None:
    """Initialize the project folder structure and all the filled in boilerplate files."""
    path = Path(path)
    setup_project_files(
        path=path,
        template=template,
        project_config=project_config,
        override=override,
    )
    setup_push_workflow(
        path=path,
        project_config=project_config,
        template=template,
        override=override,
    )
    setup_requirements(
        path=path,
        project_config=project_config,
        test=True,
        lint=True,
        override=override,
    )
    setup_scripts(
        path=path,
        template=template,
        override=override,
    )
    setup_git(
        path=path,
        project_config=project_config,
        template=template,
    )
