from collections import namedtuple
from pathlib import Path


File = namedtuple("File", "name src dst is_static")


def file(name, path, dst=None, is_static: bool = False):
    dst = dst if dst is not None else name
    return File(name=name, src=path / name, dst=dst, is_static=is_static)


# Assets paths
ASSETS_PATH = Path(__file__).parent / "assets"
TEMPLATES_PATH = ASSETS_PATH / "templates"
STATIC_FILES_PATH = ASSETS_PATH / "static"
REQUIREMENTS_PATH = ASSETS_PATH / "requirements"
WORKFLOWS_PATH = ASSETS_PATH / "workflows"

# Common files
repository = file("repository.yml", STATIC_FILES_PATH, is_static=True)
gitignore = file(".gitignore", STATIC_FILES_PATH, is_static=True)
dco = file("DCO.md", STATIC_FILES_PATH, is_static=True)
init = file("__init__.py", STATIC_FILES_PATH, is_static=True)
main = file("__main__.py", STATIC_FILES_PATH, is_static=True)
version = file("version.py", STATIC_FILES_PATH, is_static=True)
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
dockerfile = file("Dockerfile", TEMPLATES_PATH)
makefile = file("Makefile", TEMPLATES_PATH)
mlproject = file("MLproject", TEMPLATES_PATH)
readme = file("README.md", TEMPLATES_PATH)
pyproject_toml = file("pyproject.toml", TEMPLATES_PATH)

# Workflows
bump_version_wkf = file("bump-version.yml", WORKFLOWS_PATH)
lint_test_wkf = file("lint-and-pytest.yml", WORKFLOWS_PATH)
docker_test_wkf = file("test-docker.yml", WORKFLOWS_PATH)
build_pypitest_python_wkf = file("build-pure-python.yml", WORKFLOWS_PATH, "build-testpypi.yml")
build_pypitest_source_wkf = file("build-source.yml", WORKFLOWS_PATH, "build-source-testpypi.yml")
build_pypitest_wheels_wkf = file("build-wheels.yml", WORKFLOWS_PATH, "build-wheels-testpypi.yml")
release_package_wkf = file("release-package.yml", WORKFLOWS_PATH, "release-package.yml")
release_wheels_wkf = file("release-platform-wheels.yml", WORKFLOWS_PATH, "release-package.yml")

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

WORKFLOW_FILES = [bump_version_wkf, lint_test_wkf, docker_test_wkf]

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

ALL_FILES = ROOT_PATH_FILES + WORKFLOW_FILES + PYTHON_FILES + [repository]

ALL_FILE_PATHS = [str(f.src) for f in ALL_FILES]
