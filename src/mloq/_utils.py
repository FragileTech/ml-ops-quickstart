"""This module contains some utilities that are not currently used."""
import filecmp
import os
from pathlib import Path
from typing import List, Union

from omegaconf import DictConfig, OmegaConf

from mloq.files import mloq_yml


# TODO: Fix docs
def dir_trees_are_equal(dir1: Union[str, Path], dir2: Union[str, Path]) -> bool:
    """
    Compare two directories recursively. Files in each directory are \
    assumed to be equal if their names and contents are equal.

    @param dir1: First directory path
    @param dir2: Second directory path

    @return: True if the directory trees are the same and
        there were no errors while accessing the directories or files,
        False otherwise.
    """
    dirs_cmp = filecmp.dircmp(dir1, dir2)
    if (
        len(dirs_cmp.left_only) > 0
        or len(dirs_cmp.right_only) > 0
        or len(dirs_cmp.funny_files) > 0
    ):
        return False
    (_, mismatch, errors) = filecmp.cmpfiles(dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch) > 0 or len(errors) > 0:
        return False
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if not dir_trees_are_equal(new_dir1, new_dir2):
            return False
    return True


def files_are_equal(path1: Union[str, Path], path2: Union[str, Path]) -> bool:
    """
    Compare the content of two files.

    Compare two incoming files. They are assumed equal if their contents
    are the same.

    Args:
          path1: Path containing the first file to be compared.
          path2: Path containing the second file to be compared.

    Return:
         It returns True if the two given files are equal and no errors
            have arisen during the process. False otherwise.
    """
    path1 = Path(path1) if isinstance(path1, str) else path1
    path2 = Path(path2) if isinstance(path2, str) else path2
    return filecmp.cmp(path1, path2, shallow=False)


def get_generated_files(path: Union[str, Path]) -> List[Path]:
    """
    List all the files generated in the last mloq run.

    Args:
        path: path to WHAT_MLOQ_GENERATED.md file.

    Returns:
        List of Path containing the names of the files generated by mloq.
    """
    # Read file as string
    # Split file to end up with the desired file names
    pass


# TODO: Improve the Ledger class so it can also track the different directories
#  that were created, and add them under a new section in the WHAT_MLOQ_GENERATED.md


def get_generated_directories(path: Union[str, Path]) -> List[Path]:
    """
    List all the directories generated in the last mloq run.

    Args:
        path: path to WHAT_MLOQ_GENERATED.md file.

    Returns:
        List of Path containing the names of the directories generated by mloq.
    """
    pass


def check_directories_exist(paths: List[Union[str, Path]]) -> bool:
    """
    Check if the provided paths exist.

    Args:
        paths: List of paths that will be checked

    Returns:
        True if all the provided paths exist. False otherwise.
    """
    for path in paths:
        path = Path(path) if isinstance(path, str) else path
        cond1 = os.path.exists(path)
        cond2 = os.path.isfile(path) or os.path.isdir(path)
        cond3 = Path.exists(path)
        if not (cond1 and cond2 and cond3):
            print(f"The given path {path} is neither a file nor a directory.")
        return cond1 and cond2 and cond3


def get_docker_python_version(template: DictConfig) -> str:
    """Return the highest python version defined for the project."""
    max_version = list(sorted(template["python_versions"]))[-1]
    version = max_version.replace(".", "")
    return f"py{version}"


def write_config_setup(config: DictConfig, path: Union[Path, str], safe: bool = False):
    """Write setup config in a yaml file."""
    if safe:
        path = Path(path)
        path = path / mloq_yml.dst if path.is_dir() else path
    with open(path, "w") as f:
        OmegaConf.save(config, f)


def load_empty_config_setup() -> DictConfig:
    """Return a dictionary containing all the MLOQ setup config values set to None."""
    return OmegaConf.load(mloq_yml.src)
