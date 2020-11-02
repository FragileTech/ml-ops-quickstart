import os
from pathlib import Path
from shutil import copyfile

ASSETS_PATH = Path(__file__).parent / "assets"
TEMPLATES_PATH = ASSETS_PATH / "templates"
REQUIREMENTS_PATH = ASSETS_PATH / "requirements"


def _create_empty_file(filepath: Path):
    if filepath.exists():
        print(f"file {filepath.name} already exists")
        return
    with open(filepath, "w") as _:
        pass


def _copy_file(src, dst):
    if not os.path.isfile(str(dst)):
        copyfile(src, dst)
    else:
        print(f"file {dst.name} already exists")


def create_project_directories(project_name: str, root_path: Path):
    project_path = root_path / project_name
    os.makedirs(project_path, exist_ok=True)
    _create_empty_file(project_path / "__init__.py")
    _copy_file(TEMPLATES_PATH / "version.py", project_path / "version.py")
    test_path = project_path / "tests"
    os.makedirs(test_path, exist_ok=True)
    _create_empty_file(test_path / "__init__.py")


def fill_in_template(params, text):
    for k, v in params.items():
        text = text.replace("{%s}" % k, v)
    return text


def copy_and_fill_in_file(src: Path, dst: Path, params: dict):
    with open(src, "r") as f:
        text = f.read()
        filled_in_file = fill_in_template(params, text)
    with open(dst, "w") as f:
        f.write(filled_in_file)


def write_templates(params, root_path: Path, templates_path=TEMPLATES_PATH):
    for filename in os.listdir(templates_path):
        if filename in ["__init__.py", "version.py"]:
            continue
        copy_and_fill_in_file(templates_path / filename, root_path / filename, params)


def setup_project_project_files(template, root_path):
    create_project_directories(template["project_name"], root_path)
    write_templates(template, root_path)
