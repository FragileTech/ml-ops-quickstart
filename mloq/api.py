"""The api module exposes the mloq functionality to the CLI."""
import copy
from pathlib import Path
from typing import Union

from mloq.directories import copy_file, create_project_directories
from mloq.files import file as new_file, mloq_yml, ROOT_PATH_FILES, SCRIPTS, test_main
from mloq.requirements import setup_requirements
from mloq.templating import write_template
from mloq.workflows import setup_push_workflow


def init_config(path: Union[str, Path], override: bool = False, filename=None):
    """Write an empty config file to the target path."""
    repo_file = (
        mloq_yml if filename is None else new_file(mloq_yml.src, mloq_yml.src.parent, filename)
    )
    copy_file(repo_file, Path(path), override)


def requirements(
    options: Union[str, Path, list, tuple],
    path,
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


def setup_project_files(path, template: Union[Path, str, dict], override: bool = False):
    """Write the template for common repository config files."""
    path = Path(path)
    _template = copy.deepcopy(template)
    _template["project_name"] = _template["project_name"].replace("-", "_")
    project_name = _template["project_name"]
    create_project_directories(project_name=project_name, root_path=path, override=override)
    setup_root_files(template=_template, path=path, override=override)
    tests_path = path / project_name / "tests"
    write_template(test_main, params=_template, path=tests_path, override=override)


def setup_scripts(
    path: Union[str, Path], template: Union[Path, str, dict], override: bool = False
):
    """Initialize CI scripts folder files."""
    path = Path(path)
    path = path if path.name == "scripts" else path / "scripts"
    for file in SCRIPTS:
        write_template(file, params=template, path=path, override=override)


def setup_root_files(
    path: Union[str, Path], template: Union[Path, str, dict], override: bool = False
):
    """Initialize root folder files."""
    for file in ROOT_PATH_FILES:
        write_template(file, params=template, path=path, override=override)


def setup_repository(
    path: Union[str, Path], template: dict, project_config: dict, override: bool = False,
):
    """Initialize the project folder structure and all the filled in boilerplate files."""
    path = Path(path)
    setup_project_files(path=path, template=template, override=override)
    setup_push_workflow(
        project_config=project_config, path=path, template=template, override=override
    )
    requirements(
        options=project_config["requirements"], path=path, test=True, lint=True, override=override
    )
    setup_scripts(template=template, path=path, override=override)
