"""This module defines all the different assets accessible from mloq."""
from collections import namedtuple
from pathlib import Path


File = namedtuple("File", "name src dst is_static")


def file(name, path, dst=None, is_static: bool = False):
    """Define a new asset as a File namedtuple."""
    dst = dst if dst is not None else name
    return File(name=name, src=path / name, dst=dst, is_static=is_static)


# Assets paths
ASSETS_PATH = Path(__file__).parent / "assets"
TEMPLATES_PATH = ASSETS_PATH / "templates"
STATIC_FILES_PATH = ASSETS_PATH / "static"
REQUIREMENTS_PATH = ASSETS_PATH / "requirements"
WORKFLOWS_PATH = ASSETS_PATH / "workflows"

# Common files
repository = file("mloq.yml", STATIC_FILES_PATH, is_static=True)
gitignore = file(".gitignore", STATIC_FILES_PATH, is_static=True)
dco = file("DCO.md", STATIC_FILES_PATH, is_static=True)
init = file("__init__.py", STATIC_FILES_PATH, is_static=True)
main = file("__main__.py", STATIC_FILES_PATH, is_static=True)
version = file("version.py", STATIC_FILES_PATH, is_static=True)
dockerfile_aarch64 = file("Dockerfile_aarch64", STATIC_FILES_PATH, is_static=True)
build_manylinux_sh = file("build-manylinux-wheels.sh", STATIC_FILES_PATH, is_static=True)
code_of_conduct = file("code_of_conduct.md", TEMPLATES_PATH)

# Requirements files
data_science_req = file("data-science.txt", REQUIREMENTS_PATH)
data_viz_req = file("data-visualization.txt", REQUIREMENTS_PATH, is_static=True)
pytorch_req = file("pytorch.txt", REQUIREMENTS_PATH, is_static=True)
tensorflow_req = file("tensorflow.txt", REQUIREMENTS_PATH, is_static=True)
lint_req = file("requirements-lint.txt", REQUIREMENTS_PATH, is_static=True)
test_req = file("requirements-test.txt", REQUIREMENTS_PATH, is_static=True)

# Templates
mit_license = file("MIT_LICENSE", TEMPLATES_PATH, "LICENSE")
setup_py = file("setup.py", TEMPLATES_PATH)
test_main = file("test_main.txt", TEMPLATES_PATH, "test_main.py")
rename_wheels = file("rename_testpypi_wheels.py", TEMPLATES_PATH)
dockerfile = file("Dockerfile", TEMPLATES_PATH)
makefile = file("Makefile", TEMPLATES_PATH)
makefile_docker = file("makefile.docker", TEMPLATES_PATH)
mlproject = file("MLproject", TEMPLATES_PATH)
readme = file("README.md", TEMPLATES_PATH)
pyproject_toml = file("pyproject.toml", TEMPLATES_PATH)

# Workflows
push_python_wkf = file("push-python.yml", WORKFLOWS_PATH, "push.yml")
push_dist_wkf = file("push-dist.yml", WORKFLOWS_PATH, "push.yml")

ROOT_PATH_FILES = [
    dco,
    gitignore,
    code_of_conduct,
    mit_license,
    pyproject_toml,
    setup_py,
    makefile,
    dockerfile,
    mlproject,
    readme,
]

WORKFLOW_FILES = [push_dist_wkf, push_python_wkf]

PYTHON_FILES = [init, main, version]

REQUIREMENTS_FILES = [
    lint_req,
    pytorch_req,
    tensorflow_req,
    data_viz_req,
    data_science_req,
    lint_req,
    test_req,
]

SCRIPTS = [build_manylinux_sh, dockerfile_aarch64, makefile_docker, rename_wheels]

ALL_FILES = ROOT_PATH_FILES + WORKFLOW_FILES + PYTHON_FILES + [repository]

ALL_FILE_PATHS = [str(f.src) for f in ALL_FILES]
