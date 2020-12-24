"""The api module exposes the mloq functionality to the CLI."""
from pathlib import Path
from typing import Optional, Union

from mloq.directories import copy_file, create_project_directories
from mloq.files import file as new_file, repository, ROOT_PATH_FILES, SCRIPTS, test_main
from mloq.parse_config import read_config
from mloq.requirements import setup_requirements
from mloq.templating import write_template
from mloq.workflows import setup_push_workflow


def init_config(path: Union[str, Path], override: bool = False, filename=None):
    """Write an empty config file to the target path."""
    repo_file = (
        repository
        if filename is None
        else new_file(repository.src, repository.src.parent, filename)
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
    if not isinstance(options, (list, tuple)):
        options = read_config(Path(options))["requirements"]
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
    if not isinstance(template, dict):
        template = read_config(Path(template))["template"]
    path = Path(path)
    project_name = template["project_name"]
    create_project_directories(project_name=project_name, root_path=path, override=override)
    setup_root_files(template=template, path=path, override=override)
    tests_path = path / project_name / "tests"
    write_template(test_main, params=template, path=tests_path, override=override)


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
    path: Union[str, Path],
    config_file: Optional[Union[Path, str, dict]] = None,
    override: bool = False,
):
    """Initialize the project folder structure and all the filled in boilerplate files."""
    path = Path(path)
    config_file = path / "mloq.yml" if config_file is None else config_file
    config = config_file if isinstance(config_file, dict) else read_config(config_file)
    template = config["template"]
    setup_project_files(path=path, template=template, override=override)
    setup_push_workflow(config.get("workflow"), path=path, config_file=config, override=override)
    requirements(
        options=config["requirements"], path=path, test=True, lint=True, override=override
    )
    setup_scripts(template=template, path=path, override=override)
