from pathlib import Path
from typing import Tuple

import click

from mloq.command import Command
from mloq.files import PROJECT_FILES
from mloq.params import BooleanParam, config_group, ConfigParam

_PROJECT = [
    BooleanParam("disable", "Disable project command?"),
    BooleanParam("docker", "Does the project contains a docker container?"),
    ConfigParam("owner", "Github handle of the project owner"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("description", "Short description of the project"),
    ConfigParam(
        "license",
        "Project license type",
        type=click.Choice(["MIT", "Apache-2.0", "GPL-3.0", "None"], case_sensitive=False),
    ),
]


class ProjectCMD(Command):
    name = "project"
    files = tuple(PROJECT_FILES)
    CONFIG = config_group("PROJECT", _PROJECT)

    @property
    def directories(self) -> Tuple[Path]:
        project_folder = self.record.config.project.project_name.replace(" ", "_")
        return tuple([Path(project_folder) / "test"])

    def record_files(self) -> None:
        from mloq.files import init, main, makefile, readme, test_main, version

        self.record.register_file(file=readme, path=Path())
        self.record.register_file(file=makefile, path=Path())
        project_folder = Path(self.record.config.project.project_name.replace(" ", "_"))
        description = "Python package header for the project module"
        self.record.register_file(file=init, path=project_folder, description=description)
        self.record.register_file(file=main, path=project_folder)
        self.record.register_file(file=version, path=project_folder)
        description = "Python package header for the test module"
        self.record.register_file(file=init, path=project_folder / "test", description=description)
        self.record.register_file(file=test_main, path=project_folder / "test")
