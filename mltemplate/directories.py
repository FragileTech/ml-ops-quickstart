import os
from pathlib import Path
from shutil import copyfile
import sys

from mltemplate.ci.travis import export_travis_config

ASSETS_PATH = Path(__file__).parent / "assets"
COMMON_ASSETS_PATH = ASSETS_PATH / "common"
SETUP_ASSETS_PATH = ASSETS_PATH / "setup"
STYLE_ASSETS_PATH = ASSETS_PATH / "style"


def _create_empty_file(filepath: Path):
    with open(filepath, "w") as file:
        pass


def create_project_directories(project_name: str, root_path: Path):
    project_path = root_path / project_name
    os.makedirs(project_path, exist_ok=True)
    _create_empty_file(project_path / "__init__.py")
    copyfile(SETUP_ASSETS_PATH / "version.py", project_path / "version.py")
    test_path = project_path / "test"
    os.makedirs(test_path, exist_ok=True)
    _create_empty_file(test_path / "__init__.py")


def fill_in_template(params, text):
    for k, v in params.items():
        key = f"%{k.upper()}"
        text = text.replace(key, v)
    return text


def copy_and_fill_in_file(src: Path, dst: Path, params: dict):
    with open(src, "r") as f:
        text = f.read()
        filled_in_file = fill_in_template(params, text)
    with open(dst, "w") as f:
        f.write(filled_in_file)


def add_style_check(params, root_path: Path, doc_linter: bool = True):
    for filename in os.listdir(STYLE_ASSETS_PATH):
        if filename == ".pylintrc" and not doc_linter:
            continue
        copy_and_fill_in_file(STYLE_ASSETS_PATH / filename, root_path / filename, params)


def create_common_files(params, root_path: Path):
    for filename in os.listdir(COMMON_ASSETS_PATH):
        copy_and_fill_in_file(COMMON_ASSETS_PATH / filename, root_path / filename, params)


def setup_project(params, root_path):
    template = params["template"]
    ci_stages = params["ci"]["ci_stages"]
    python_versions = params["ci"]["python_versions"]
    create_project_directories(template["project_name"], root_path)
    create_common_files(template, root_path)
    add_style_check(template, root_path, False)
    export_travis_config(root_path, template, ci_stages, python_versions)
    copy_and_fill_in_file(SETUP_ASSETS_PATH / "setup.py", root_path / "setup.py", template)
    copy_and_fill_in_file(COMMON_ASSETS_PATH / "Makefile", root_path / "Makefile", template)
