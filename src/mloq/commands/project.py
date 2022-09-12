"""Mloq project command implementation."""
from pathlib import Path
from typing import Tuple

from mloq.command import Command
from mloq.config.param_patch import param
from mloq.files import ASSETS_PATH, file, makefile


PROJECT_ASSETS_PATH = ASSETS_PATH / "project"
readme = file("README.md", PROJECT_ASSETS_PATH, "README")
gitignore = file(
    ".gitignore",
    PROJECT_ASSETS_PATH,
    "list of files and directories ignored by Git operations",
    is_static=True,
)
pre_commit_hook = file(
    ".pre-commit-config.yaml",
    PROJECT_ASSETS_PATH,
    "Git pre-commit hooks configuration",
    is_static=True,
)
init = file(
    "init.txt",
    PROJECT_ASSETS_PATH,
    "Python package header",
    dst="__init__.py",
    is_static=True,
)
main = file(
    "main.txt",
    PROJECT_ASSETS_PATH,
    "Python package executable entry point",
    dst="__main__.py",
    is_static=True,
)
test_main = file(
    "test_main.txt",
    PROJECT_ASSETS_PATH,
    "Unit test of the python package executable entry point",
    dst="test_main.py",
    is_static=False,
)
test_req = file(
    "requirements-test.txt",
    PROJECT_ASSETS_PATH,
    "list of exact versions of the packages needed to run your test suite",
    is_static=True,
)
version = file(
    "version.txt",
    PROJECT_ASSETS_PATH,
    "defines the version of the package that is incremented on each push",
    dst="version.py",
    is_static=True,
)
code_of_conduct = file(
    "CODE_OF_CONDUCT.md",
    PROJECT_ASSETS_PATH,
    "behavioral rules and norms in open source projects",
)
codecov = file(
    ".codecov.yml",
    PROJECT_ASSETS_PATH,
    "configuration of CodeCov service to track the code coverage",
)
contributing = file(
    "CONTRIBUTING.md",
    PROJECT_ASSETS_PATH,
    "technical manual on how to contrib to the open source project",
)

PROJECT_FILES = [
    codecov,
    gitignore,
    readme,
    makefile,
    init,
    main,
    test_main,
    version,
    test_req,
    pre_commit_hook,
    contributing,
    code_of_conduct,
]

# TODO: select which files are created in config
# package folders: __init__, __main__, version
# contributing
# codecov
# gitignore
# makefile
# pre commit


class ProjectCMD(Command):
    """Implement the functionality of the project Command."""

    cmd_name = "project"
    files = tuple(PROJECT_FILES)
    disable = param.Boolean(default=False, doc="Disable project command?")
    project_name = param.String("${globals.project_name}", doc="Select project name")
    owner = param.String("${globals.owner}", doc="Github handle of the project owner")
    description = param.String("${globals.description}", doc="Short description of the project")
    project_url = param.String("${globals.project_url}", doc="GitHub project url")
    license = param.String("MIT", doc="Project license type")
    tests = param.Boolean(True, doc="Add support for pytest")

    @property
    def directories(self) -> Tuple[Path]:
        """Tuple containing Paths objects representing the directories created by the command."""
        project_folder = self.record.config.project.project_name.replace(" ", "_")

        return tuple([Path("src") / project_folder, Path("tests")])

    def record_files(self) -> None:
        """Register the files that will be generated by mloq."""
        self.record.register_file(file=readme, path=Path())
        self.record.register_file(file=makefile, path=Path())
        project_folder = Path("src") / self.record.config.project.project_name.replace(" ", "_")
        description = "Python package header for the project module"
        self.record.register_file(file=init, path=project_folder, description=description)
        self.record.register_file(file=main, path=project_folder)
        self.record.register_file(file=version, path=project_folder)
        description = "Python package header for the test module"
        self.record.register_file(file=init, path=Path("tests"), description=description)
        self.record.register_file(file=test_main, path=Path("tests"))
        root_files = [
            readme,
            makefile,
            test_req,
            pre_commit_hook,
            codecov,
            gitignore,
            code_of_conduct,
            contributing,
        ]
        for _file in root_files:
            self.record.register_file(file=_file, path=Path())
