"""This module defines common functionality for dealing with directories and files."""
import os
from pathlib import Path
from shutil import copyfile
from typing import Optional, Union

from omegaconf import DictConfig

from mloq import _logger
from mloq.failure import Failure
from mloq.files import File, init, Ledger, main, test_main, version
from mloq.templating import write_template


def copy_file(
    file: File,
    path: Union[Path, str],
    ledger: Ledger,
    overwrite: bool = False,
    description: Optional[str] = None,
) -> None:
    """
    Copy the file from src into dst.

    Args:
        file: File object representing the file that will be copied.
        path: Path to the destination of the copied file.
        ledger: Book keeper to keep track of the generated files.
        overwrite: If False, copy the file if it does not already exists in the \
                   target path. If True, overwrite the target file if it is already present.
        description: Description of the file that will be recorded by the Ledger.
    Returns:
        None.
    """
    target = path / file.dst
    if not os.path.isfile(str(target)) or overwrite:
        ledger.register(file, description=description)
        copyfile(file.src, target)
    else:
        _logger.debug(f"file {file.dst} already exists in {target}")


def create_project_skeleton(
    root_path: Path,
    config: DictConfig,
    ledger: Ledger,
    overwrite: bool = False,
) -> None:
    """
    Initialize the folder structure of a new Python project together with a bare minimum set of \
    code files.

    It creates a directory for the project containing an empty __init__.py file, and a \
    tests folder inside it with its corresponding __init__.py file. This function will only \
    create new files and folders in case they don't already exist, but it won't overwrite any \
    existing file.

    Args:
        root_path: Absolute path where the new project folder will be created.
        config: Contains all the parameters that define how the project will be set up.
        ledger: Book keeper for the generated files.
        overwrite: If False, copy the file if it does not already exists in the \
                   target path. If True, overwrite the target file if it is already present.

    Returns:
        None.
    """
    project_name = config.template.project_name
    # Project dir
    try:
        project_path = root_path / project_name
        os.makedirs(project_path, exist_ok=True)
        description = "Python package header for the project module"
        copy_file(init, project_path, ledger, overwrite, description=description)
        copy_file(version, project_path, ledger, overwrite)
        write_template(main, config=config, path=project_path, ledger=ledger, overwrite=overwrite)
        # Test dir inside project
        test_path = project_path / "tests"
        os.makedirs(test_path, exist_ok=True)
        write_template(
            test_main,
            config=config,
            path=test_path,
            ledger=ledger,
            overwrite=overwrite,
        )
        description = "Python package header for the test module"
        copy_file(init, test_path, ledger, overwrite, description=description)
    except (PermissionError, FileNotFoundError) as e:
        raise Failure() from e


def create_github_actions_directories(root_path: Union[str, Path]) -> None:
    """
    Initialize the folder structure for using GitHub actions workflows.

    It creates a .github directory on the target path, with an empty workflows \
    directory inside it, so the .github/workflows directory is ready to add GitHub \
    actions workflows. This function will only create new folders in case they don't already exist.

    Args:
        root_path: Absolute path where the .github folder will be crated.

    Returns:
        None.
    """
    gha_path = Path(root_path) / ".github"
    os.makedirs(gha_path, exist_ok=True)
    workflows_path = gha_path / "workflows"
    os.makedirs(workflows_path, exist_ok=True)


def create_docs_directories(root_path: Union[str, Path]) -> None:
    """
    Create the documentation directory structure.

    It creates a docs folder containing an images folder and a source folder. \
    The source folder contains an images folder, an _static folder, and a markdown folder.

    Args:
        root_path: Absolute path where the docs folder will be crated.

    Returns:
        None.
    """
    docs_path = Path(root_path) / "docs"
    os.makedirs(docs_path, exist_ok=True)
    imgs_path = docs_path / "images"
    os.makedirs(imgs_path, exist_ok=True)
    source_path = docs_path / "source"
    os.makedirs(source_path, exist_ok=True)
    static_path = source_path / "_static"
    os.makedirs(static_path, exist_ok=True)
    markdown_path = source_path / "markdown"
    os.makedirs(markdown_path, exist_ok=True)
