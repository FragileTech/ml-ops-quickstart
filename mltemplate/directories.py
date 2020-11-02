import os
from pathlib import Path
from shutil import copyfile

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('mltemplate', 'assets/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

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


def render_template(name: str, params: dict):
    template = env.get_template(name)
    return template.render(**params)


def write_templates(params, root_path: Path, templates_path=TEMPLATES_PATH):
    for filename in os.listdir(templates_path):
        if filename in ["__init__.py", "version.py"]:
            continue
        rendered = render_template(filename, params)
        with open(root_path / filename, "w") as f:
            f.write(rendered)


def setup_project_project_files(template_params, root_path):
    create_project_directories(template_params["project_name"], root_path)
    write_templates(template_params, root_path)
