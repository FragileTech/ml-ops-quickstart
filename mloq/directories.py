"""This module defines common functionality for dealing with directories and files."""
import os
from pathlib import Path
from shutil import copyfile
from typing import Union

from mloq.files import File, init, main, version


def create_empty_file(filepath: Path) -> None:
    """
    Create an empty file in the target path.

    Args:
        filepath: Absolute path to the file that will be created.

    Returns:
        None
    """
    if filepath.exists():
        print(f"file {filepath.name} already exists")
        return
    with open(filepath, "w") as _:
        pass


def read_file(file: File) -> str:
    """Return and string with the content of the provided file."""
    with open(file.src, "r") as f:
        return f.read()


def copy_file(file: File, path: Union[Path, str], override: bool = False) -> None:
    """
    Copy the file from src into dst.

    Args:
        file: File object representing the file that will be copied.
        path: Path to the destination of the copied file.
        override: If False, copy the file if it does not already exists in the \
                  target path. If True, override the target file if it is already present.
    Returns:
        None.
    """
    target = path / file.dst
    if not os.path.isfile(str(target)) or override:
        copyfile(file.src, target)
    else:
        print(f"file {file.name} already exists in {target}")


def create_project_directories(project_name: str, root_path: Path, override: False) -> None:
    """
    Initialize the folder structure of a new Python project.

    It creates a directory for the project containing an empty __init__.py file, and a \
    tests folder inside it with its corresponding __init__.py file. This function will only \
    create new files and folders in case they don't already exist, but it won't override any \
    existing file.

    Args:
        project_name: Name of the project. This is the name of the directory that will be created.
        root_path: Absolute path where the new project folder will be created.
        override: If False, copy the file if it does not already exists in the \
                  target path. If True, override the target file if it is already present.

    Returns:
        None.
    """
    # Project dir
    project_path = root_path / project_name
    os.makedirs(project_path, exist_ok=True)
    copy_file(init, project_path, override)
    copy_file(version, project_path, override)
    copy_file(main, project_path, override)
    # Test dir inside project
    test_path = project_path / "tests"
    os.makedirs(test_path, exist_ok=True)
    copy_file(init, test_path, override)
    # Scripts dir
    scripts_path = root_path / "scripts"
    os.makedirs(scripts_path, exist_ok=True)


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
