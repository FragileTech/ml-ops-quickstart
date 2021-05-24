"""The api module exposes the mloq functionality to the CLI."""
from pathlib import Path
from typing import List, Tuple, Union

from omegaconf import DictConfig

from mloq.files import (
    dockerfile,
    DOCS_FILES,
    Ledger,
    LICENSES,
    mlproject,
    OPEN_SOURCE_FILES,
    ROOT_PATH_FILES,
    setup_py,
    what_mloq_generated,
)
from mloq.git import setup_git
from mloq.requirements import install_requirements, write_requirements
from mloq.skeleton import create_docs_directories, create_project_skeleton
from mloq.templating import write_template
from mloq.workflows import setup_push_workflow


def setup_requirements(
    path: Union[Path, str],
    config: DictConfig,
    ledger: Ledger,
    lint: bool = True,
    test: bool = True,
    install: Union[str, Tuple[str], List[str], None] = None,
    overwrite: bool = False,
) -> None:
    """
    Write requirements files and install them if requested.

    This method writes the necessary requirement files (according to the
    selected options) of the new project. These files lists the exact
    versions of the packages needed to run the project. The method also
    allows installing the dependencies listed in the target requirements
    files.

    Args:
         path: Target folder where the configuration files will be written.
         config: DictConfig containing the selected project configuration.
         ledger: Ledger object. Keeps track of the generated files.
         lint: If True, writes the requirement-lint.txt file on the target
            folder.
         test: If True, writes the requirement-test.txt file on the target
            folder.
         install: Lists the target requirements files to be installed.
         overwrite: If True, overwrites existing files. Otherwise files
            that already exists will not be modified.
    """
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
        overwrite=overwrite,
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
    config: DictConfig,
    ledger: Ledger,
    overwrite: bool = False,
) -> None:
    """
    Write the template for common repository config files.

    This method initializes the structure of the new project, including
    primary code files. Additionally, it creates 'template'-related
    files (those concerning common repository configuration files) on the
    target folder.

    Args:
         path: Target folder where the generated files will be written.
         config: DictConfig containing the selected project configuration.
         ledger: Ledger object. Keeps track of the generated files.
         overwrite: If True, overwrites existing files. Otherwise files
            that already exists will not be modified.
    """
    path = Path(path)
    original_project_name = config.template.project_name
    config.template.project_name = config.template.project_name.replace("-", "_")
    try:
        create_project_skeleton(config=config, root_path=path, ledger=ledger, overwrite=overwrite)
        setup_root_files(
            config=config,
            path=path,
            overwrite=overwrite,
            ledger=ledger,
        )
    finally:
        config.template.project_name = original_project_name


def setup_root_files(
    path: Union[str, Path],
    config: DictConfig,
    ledger: Ledger,
    overwrite: bool = False,
) -> None:
    """
    Initialize root folder files.

    It writes repository files using as input the incoming DictConfig,
    which summarizes the options chosen by the user.

    Args:
         path: Target folder where the generated files will be written.
         config: DictConfig containing the selected project configuration.
         ledger: Ledger object. Keeps track of the generated files.
         overwrite: If True, overwrites existing files. Otherwise files
            that already exists will not be modified.
    """
    for file in ROOT_PATH_FILES:
        write_template(file, config=config, path=path, ledger=ledger, overwrite=overwrite)
    if config.project.get("docker"):
        write_template(dockerfile, config=config, path=path, ledger=ledger, overwrite=overwrite)
    if config.project.get("mlflow"):
        write_template(mlproject, config=config, path=path, ledger=ledger, overwrite=overwrite)
    if config.project.get("open_source"):
        for file in OPEN_SOURCE_FILES:
            write_template(file, config=config, path=path, ledger=ledger, overwrite=overwrite)
        license = config.template.license
        write_template(
            LICENSES[license],
            config=config,
            path=path,
            ledger=ledger,
            overwrite=overwrite,
        )
    else:
        license = "proprietary"
    license_classifiers = {
        "MIT": "License :: OSI Approved :: MIT License",
        "Apache-2.0": "License :: OSI Approved :: Apache Software License",
        "GPL-3.0": "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "proprietary": "License :: Other/Proprietary License",
    }
    license_classifer = license_classifiers[license]
    config = DictConfig({**config, "license_classifier": license_classifer})
    write_template(setup_py, config=config, path=path, ledger=ledger, overwrite=overwrite)


def dump_ledger(
    path: Union[str, Path],
    config: DictConfig,
    ledger: Ledger,
    overwrite: bool = False,
) -> None:
    """
    Write the summary of the generated files.

    This method collects the elements stored in ledger to create a markdown
    document that summarizes all the files generated by the MLOQ application.

    Args:
         path: Target folder where the generated files will be written.
         config: DictConfig containing the selected project configuration.
         ledger: Ledger object. Keeps track of the generated files.
         overwrite: If True, overwrites existing files. Otherwise files
            that already exists will not be modified.
    """
    config.template = DictConfig({**config.template, "generated_files": ledger.files})
    write_template(
        what_mloq_generated,
        config=config,
        path=path,
        ledger=ledger,
        overwrite=overwrite,
    )


def setup_docs(
    path: Union[str, Path],
    config: DictConfig,
    ledger: Ledger,
    overwrite: bool = False,
) -> None:
    """
    Configure the project documentation.

    When calling this function, it generates a documentation folder that
    contains necessary configuration files (requirement lists, 'make' commands,
    sphinx configurations) for building the documentation of the project.

    Args:
         path: Target folder where the generated files will be written.
         config: DictConfig containing the selected project configuration.
         ledger: Ledger object. Keeps track of the generated files.
         overwrite: If True, overwrites existing files. Otherwise files
            that already exists will not be modified.
    """
    if not config.project.get("docs", False):
        return
    create_docs_directories(root_path=path)
    source_files = {"conf.txt", "index.md"}
    docs_path = Path(path) / "docs"
    for file in DOCS_FILES:
        out_path = (docs_path / "source") if file.name in source_files else docs_path
        write_template(file, config=config, path=out_path, ledger=ledger, overwrite=overwrite)


def setup_project(
    path: Union[str, Path],
    config: DictConfig,
    overwrite: bool = False,
) -> None:
    """
    Initialize the project folder structure and all the filled-in boilerplate files.

    It calls the setup methods to generate (on the target path) the folder
    structure of the project, as well as repository files, requirement
    lists, and Github workflows (if requested).

    Args:
         path: Target folder where the generated files will be written.
         config: DictConfig containing the selected project configuration.
         overwrite: If True, overwrites existing files. Otherwise files
            that already exists will not be modified.
    """
    assert isinstance(config, DictConfig)
    path = Path(path)
    ledger = Ledger()
    setup_project_files(path=path, config=config, ledger=ledger, overwrite=overwrite)
    setup_push_workflow(path=path, config=config, ledger=ledger, overwrite=overwrite)
    setup_docs(path=path, config=config, ledger=ledger, overwrite=overwrite)
    setup_requirements(
        path=path,
        config=config,
        test=True,
        lint=True,
        ledger=ledger,
        overwrite=overwrite,
    )
    dump_ledger(path=path, config=config, ledger=ledger, overwrite=overwrite)
    setup_git(path=path, config=config)


def docs_project(
    path: Union[str, Path],
    config: DictConfig,
    overwrite: bool = False,
) -> None:
    """
    Initialize the project folder structure and all the documentation files.

    It calls the documentation setup method to generate (on the target
    path) the documentation files required by the project. This folder
    will contain configuration files (requirement lists, 'make' commands,
    sphinx configurations) needed for building the documentation of
    the project.

    Args:
         path: Target folder where the generated files will be written.
         config: DictConfig containing the selected project configuration.
         overwrite: If True, overwrites existing files. Otherwise files
            that already exists will not be modified.
    """
    assert isinstance(config, DictConfig)
    path = Path(path)
    ledger = Ledger()
    setup_docs(path=path, config=config, ledger=ledger, overwrite=overwrite)
    dump_ledger(path=path, config=config, ledger=ledger, overwrite=overwrite)


def package_project(
    path: Union[str, Path],
    config: DictConfig,
    overwrite: bool = False,
) -> None:
    """
    Initialize the project folder structure and repository files.

    It calls the setup project method to initialize the skeleton of the
    new project and create repository code files. Using 'config' as input
    dictionary, this method fills in core assets to generate primary files
    on the target path.

    Args:
        path: Target folder where the generated files will be written.
        config: DictConfig containing the selected project configuration.
        overwrite: If True, overwrites existing files. Otherwise files
            that already exists will not be modified.
    """
    assert isinstance(config, DictConfig)
    path = Path(path)
    ledger = Ledger()
    setup_project_files(path=path, config=config, ledger=ledger, overwrite=overwrite)
    dump_ledger(path=path, config=config, ledger=ledger, overwrite=overwrite)
