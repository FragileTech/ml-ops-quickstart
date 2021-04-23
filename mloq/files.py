"""This module defines all the different assets accessible from mloq."""
from pathlib import Path
import sys
from typing import List, NamedTuple, Optional, Tuple, Union


class File(NamedTuple):
    """Generated project file."""

    name: str
    src: Path
    dst: Path
    description: str
    is_static: bool


def file(
    name: str,
    path: Union[Path, str],
    description: Optional[str] = None,
    dst: Optional[Union[Path, str]] = None,
    is_static: bool = False,
):
    """Define a new asset as a File namedtuple."""
    if description is None:
        print("FIXME: %s must have a description" % name, file=sys.stderr)
        description = "TODO"
    dst = Path(dst) if dst is not None else name
    return File(
        name=name,
        src=Path(path) / name,
        dst=dst,
        description=description,
        is_static=is_static,
    )


class Ledger:
    """Keep track of the generated files."""

    def __init__(self):
        """Initialize a new instance of the Ledger class."""
        self._files = []

    @property
    def files(self) -> List[Tuple[str, str]]:
        """Return the list of generated file names."""
        return [(str(f), d) for f, d in sorted(self._files)]

    def register(self, file: Union[File, str, Path], description: Optional[str] = None) -> None:
        """Append another generated file to the book."""
        if isinstance(file, File):
            description = file.description
            file = file.dst
        else:
            assert description is not None
        self._files.append((Path(file), description))


# Assets paths
ASSETS_PATH = Path(__file__).parent / "assets"
TEMPLATES_PATH = ASSETS_PATH / "templates"
STATIC_FILES_PATH = ASSETS_PATH / "static"
REQUIREMENTS_PATH = ASSETS_PATH / "requirements"
WORKFLOWS_PATH = ASSETS_PATH / "workflows"

# Common files
mloq_yml = file(
    "mloq.yml",
    STATIC_FILES_PATH,
    "mloq configuration, you can safely remove it if you don't plan to upgrade",
    is_static=True,
)
gitignore = file(
    ".gitignore",
    STATIC_FILES_PATH,
    "list of files and directories ignored by Git operations",
    is_static=True,
)
pre_commit_hook = file(
    ".pre-commit-config.yaml",
    STATIC_FILES_PATH,
    "Git pre-commit hooks configuration",
    is_static=True,
)
dco = file(
    "DCO.md",
    STATIC_FILES_PATH,
    "Developer Certificate of Origin - needed in open source projects to certify that "
    "the incoming contributions are legitimate",
    is_static=True,
)
init = file(
    "init.txt",
    STATIC_FILES_PATH,
    "Python package header",
    dst="__init__.py",
    is_static=True,
)
main = file(
    "main.txt",
    STATIC_FILES_PATH,
    "Python package executable entry point",
    dst="__main__.py",
    is_static=True,
)
test_main = file(
    "test_main.txt",
    STATIC_FILES_PATH,
    "Unit test of the python package executable entry point",
    dst="test_main.py",
    is_static=False,
)
version = file(
    "version.txt",
    STATIC_FILES_PATH,
    "defines the version of the package that is incremented on each push",
    dst="version.py",
    is_static=True,
)
dockerfile_aarch64 = file(
    "Dockerfile_aarch64",
    STATIC_FILES_PATH,
    "Dockerfile to build for aarch64 hardware",
    is_static=True,
)
build_manylinux_sh = file(
    "build-manylinux-wheels.sh",
    STATIC_FILES_PATH,
    "script to build universal Linux wheels",
    is_static=True,
)
code_of_conduct = file(
    "CODE_OF_CONDUCT.md",
    TEMPLATES_PATH,
    "behavioral rules and norms in open source projects",
)

# Requirements files
data_science_req = file(
    "data-science.txt",
    REQUIREMENTS_PATH,
    "list of commonly used data science libraries",
)
data_viz_req = file(
    "data-visualization.txt",
    REQUIREMENTS_PATH,
    "list of commonly used visualization libraries",
    is_static=True,
)
pytorch_req = file(
    "pytorch.txt",
    REQUIREMENTS_PATH,
    "Pytorch deep learning libraries",
    is_static=True,
)
tensorflow_req = file(
    "tensorflow.txt",
    REQUIREMENTS_PATH,
    "Tensorflow deep learning libraries",
    is_static=True,
)
lint_req = file(
    "requirements-lint.txt",
    REQUIREMENTS_PATH,
    "list of exact versions of the packages used to check your code style",
    is_static=True,
)
test_req = file(
    "requirements-test.txt",
    REQUIREMENTS_PATH,
    "list of exact versions of the packages needed to run your test suite",
    is_static=True,
)
dogfood_req = file(
    "dogfood.txt",
    REQUIREMENTS_PATH,
    "list of mock requirements for testing purposes",
    is_static=True,
)

# Templates
mit_license = file("MIT_LICENSE", TEMPLATES_PATH, "license of the project", dst="LICENSE")
apache_license = file("APACHE_LICENSE", TEMPLATES_PATH, "license of the project", dst="LICENSE")
gpl_license = file(
    "GPL_LICENSE",
    STATIC_FILES_PATH,
    "license of the project",
    dst="LICENSE",
    is_static=True,
)
setup_py = file(
    "setup.txt",
    TEMPLATES_PATH,
    "Python package installation metadata",
    dst="setup.py",
)
rename_wheels = file(
    "rename_testpypi_wheels.txt",
    TEMPLATES_PATH,
    "script to work with the test PyPi - test Python package repository",
    dst="rename_testpypi_wheels.py",
)
dockerfile = file("Dockerfile", TEMPLATES_PATH, "Dockerfile to install the project")
makefile = file("Makefile", TEMPLATES_PATH, "common make commands for development")
mlproject = file("MLproject", TEMPLATES_PATH, "file defining MLFlow projects")
readme = file("README.md", TEMPLATES_PATH, "README")
contributing = file(
    "CONTRIBUTING.md",
    TEMPLATES_PATH,
    "technical manual on how to contrib to the open source project",
)
pyproject_toml = file(
    "pyproject.toml",
    TEMPLATES_PATH,
    "configuration of various development tools: linters, formatters",
)
codecov = file(
    ".codecov.yml",
    TEMPLATES_PATH,
    "configuration of CodeCov service to track the code coverage",
)
what_mloq_generated = file("WHAT_MLOQ_GENERATED.md", TEMPLATES_PATH, "this file")

# Workflows
push_python_wkf = file(
    "push-python.yml",
    WORKFLOWS_PATH,
    "GitHub Actions continuous integration workflow file",
    dst="push.yml",
)
push_dist_wkf = file(
    "push-dist.yml",
    WORKFLOWS_PATH,
    "GitHub Actions continuous integration workflow file",
    dst="push.yml",
)

ROOT_PATH_FILES = [
    gitignore,
    pre_commit_hook,
    pyproject_toml,
    makefile,
    readme,
    codecov,
]

OPEN_SOURCE_FILES = [dco, contributing, code_of_conduct]

LICENSES = {
    "MIT": mit_license,
    "Apache-2.0": apache_license,
    "GPL-3.0": gpl_license,
}

WORKFLOW_FILES = [push_dist_wkf, push_python_wkf]

PYTHON_FILES = [init, main, test_main, version]

REQUIREMENTS_FILES = [
    lint_req,
    pytorch_req,
    tensorflow_req,
    data_viz_req,
    data_science_req,
    lint_req,
    test_req,
]

SCRIPTS = [build_manylinux_sh, rename_wheels]

ALL_FILES = ROOT_PATH_FILES + WORKFLOW_FILES + PYTHON_FILES + [mloq_yml]

ALL_FILE_PATHS = [str(f.src) for f in ALL_FILES]


def read_file(file: File) -> str:
    """Return and string with the content of the provided file."""
    with open(file.src, "r") as f:
        return f.read()
