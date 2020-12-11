from pathlib import Path
from typing import Optional, Union

from mltemplate.directories import (
    copy_file,
    create_github_actions_directories,
    create_project_directories,
)
from mltemplate.files import repository, ROOT_PATH_FILES
from mltemplate.parse_config import read_config
from mltemplate.templating import write_template
from mltemplate.workflows import setup_workflows


def init_config(path: Path, override: bool = False):
    copy_file(repository, path, override)


def init_repository(path, config_file: Optional[Union[Path, str]] = None, override: bool = False):
    config_file = path / "repository.yaml" if config_file is None else config_file
    config = read_config(config_file)
    template = config["template"]
    create_github_actions_directories(path)
    create_project_directories(
        project_name=template["project_name"], root_path=path, override=override
    )
    for file in ROOT_PATH_FILES:
        write_template(file, params=template, target_path=path, override=override)
    if "workflows" in config:
        setup_workflows(config["workflows"], root_path=path, params=template, override=override)
