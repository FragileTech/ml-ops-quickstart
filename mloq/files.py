from collections import namedtuple
from pathlib import Path


File = namedtuple("File", "name src is_static")
# Assets paths
ASSETS_PATH = Path(__file__).parent / "assets"
TEMPLATES_PATH = ASSETS_PATH / "templates"
STATIC_FILES_PATH = ASSETS_PATH / "static"
REQUIREMENTS_PATH = ASSETS_PATH / "requirements"
WORKFLOWS_PATH = ASSETS_PATH / "workflows"

# Static files
repository = File(name="repository.yml", src=STATIC_FILES_PATH / "repository.yml", is_static=True)
gitignore = File(name=".gitignore", src=STATIC_FILES_PATH / ".gitignore", is_static=True)
dco = File(name="DCO.md", src=STATIC_FILES_PATH / "DCO.md", is_static=True)
init = File(name="__init__.py", src=STATIC_FILES_PATH / "__init__.py", is_static=True)
version = File(name="version.py", src=STATIC_FILES_PATH / "version.py", is_static=True)
main = File(name="__main__.py", src=STATIC_FILES_PATH / "__main__.py", is_static=True)
code_of_conduct = File(
    name="code_of_conduct.md", src=TEMPLATES_PATH / "code_of_conduct.md", is_static=False
)

# Requirements files
data_science_req = File(
    name="data-science.txt", src=REQUIREMENTS_PATH / "data-science.txt", is_static=True
)
data_viz_req = File(
    name="data-visualization.txt",
    src=REQUIREMENTS_PATH / "data-visualization.txt",
    is_static=True,
)
pytorch_req = File(name="pytorch.txt", src=REQUIREMENTS_PATH / "pytorch.txt", is_static=True)
tensorflow_req = File(
    name="tensorflow.txt", src=REQUIREMENTS_PATH / "tensorflow.txt", is_static=True
)
lint_req = File(
    name="requirements-lint.txt", src=REQUIREMENTS_PATH / "requirements-lint.txt", is_static=True,
)
test_req = File(
    name="requirements-test.txt", src=REQUIREMENTS_PATH / "requirements-test.txt", is_static=True,
)

# Templates
dockerfile = File(name="Dockerfile", src=TEMPLATES_PATH / "Dockerfile", is_static=False)
mit_license = File(name="LICENSE", src=TEMPLATES_PATH / "LICENSE", is_static=False)
makefile = File(name="Makefile", src=TEMPLATES_PATH / "Makefile", is_static=False)
mlproject = File(name="MLproject", src=TEMPLATES_PATH / "MLproject", is_static=False)
readme = File(name="README.md", src=TEMPLATES_PATH / "README.md", is_static=False)
setup_py = File(name="setup.py", src=TEMPLATES_PATH / "setup.py", is_static=False)
pyproject_toml = File(
    name="pyproject.toml", src=TEMPLATES_PATH / "pyproject.toml", is_static=False
)

# Workflows
bump_version_wkf = File(
    name="bump-version.yml", src=WORKFLOWS_PATH / "bump-version.yml", is_static=False
)
lint_test_wkf = File(
    name="lint-and-test.yml", src=WORKFLOWS_PATH / "lint-and-test.yml", is_static=False
)
docker_test_wkf = File(
    name="test-docker.yml", src=WORKFLOWS_PATH / "test-docker.yml", is_static=False
)

ROOT_PATH_FILES = (
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
)
