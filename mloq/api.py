"""The api module exposes the mloq functionality to the CLI."""
from pathlib import Path
from typing import List, Tuple, Union

from omegaconf import DictConfig

from mloq.config import Config
from mloq.directories import create_project_directories
from mloq.files import (
    dockerfile,
    dockerfile_aarch64,
    Ledger,
    mlproject,
    OPEN_SOURCE_FILES,
    ROOT_PATH_FILES,
    SCRIPTS,
    setup_py,
    what_mloq_generated,
)
from mloq.git import setup_git
from mloq.requirements import install_requirements, write_requirements
from mloq.templating import write_template
from mloq.workflows import setup_push_workflow


def setup_requirements(
    path: Union[Path, str],
    config: Config,
    ledger: Ledger,
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
    options = config.project.get("requirements", ["empty"])
    write_requirements(
        out_path=path,
        options=options,
        test=test,
        lint=lint,
        ledger=ledger,
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
    config: Config,
    ledger: Ledger,
    override: bool = False,
) -> None:
    """Write the template for common repository config files."""
    path = Path(path)
    original_project_name = config.template.project_name
    project_name = config.template.project_name = config.template.project_name.replace("-", "_")
    try:
        create_project_directories(project_name=project_name, root_path=path, override=override)
        setup_root_files(
            config=config,
            path=path,
            override=override,
            ledger=ledger,
        )
    finally:
        config.template.project_name = original_project_name


def setup_scripts(
    path: Union[str, Path],
    config: Config,
    ledger: Ledger,
    override: bool = False,
) -> None:
    """Initialize CI scripts folder files."""
    path = Path(path)
    path = path if path.name == "scripts" else path / "scripts"
    for file in SCRIPTS:
        write_template(file, config=config, path=path, ledger=ledger, override=override)
    if config["project"].get("docker"):
        write_template(
            dockerfile_aarch64,
            config=config,
            path=path,
            ledger=ledger,
            override=override,
        )


def setup_root_files(
    path: Union[str, Path],
    config: Config,
    ledger: Ledger,
    override: bool = False,
) -> None:
    """Initialize root folder files."""
    for file in ROOT_PATH_FILES:
        write_template(file, config=config, path=path, ledger=ledger, override=override)
    if config.project.get("docker"):
        write_template(dockerfile, config=config, path=path, ledger=ledger, override=override)
    if config.project.get("mlflow"):
        write_template(mlproject, config=config, path=path, ledger=ledger, override=override)
    if config.project.get("open_source"):
        for file in OPEN_SOURCE_FILES:
            write_template(file, config=config, path=path, ledger=ledger, override=override)
    propietary_classifier = "License :: Other/Proprietary License"
    license_classifiers = {"mit": "License :: OSI Approved :: MIT License"}
    license_classifer = license_classifiers.get(config.template["license"], propietary_classifier)
    config = DictConfig({**config, "license_classifier": license_classifer})
    write_template(setup_py, config=config, path=path, ledger=ledger, override=override)


def dump_ledger(
    path: Union[str, Path],
    config: Config,
    ledger: Ledger,
    override: bool = False,
) -> None:
    """Write the summary of the generated files."""
    config.template = DictConfig({**config.template, "generated_files": ledger.files})
    write_template(
        what_mloq_generated,
        config=config,
        path=path,
        ledger=ledger,
        override=override,
    )


def setup_project(
    path: Union[str, Path],
    config: Config,
    override: bool = False,
) -> None:
    """Initialize the project folder structure and all the filled in boilerplate files."""
    assert isinstance(config, Config)
    path = Path(path)
    ledger = Ledger()
    setup_project_files(
        path=path,
        config=config,
        ledger=ledger,
        override=override,
    )
    setup_push_workflow(
        path=path,
        config=config,
        ledger=ledger,
        override=override,
    )
    setup_requirements(
        path=path,
        config=config,
        test=True,
        lint=True,
        ledger=ledger,
        override=override,
    )
    setup_scripts(
        path=path,
        config=config,
        ledger=ledger,
        override=override,
    )
    dump_ledger(
        path=path,
        ledger=ledger,
        config=config,
        override=override,
    )
    setup_git(
        path=path,
        config=config,
    )
