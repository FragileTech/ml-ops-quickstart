"""Setup Git repository for the project."""


from pathlib import Path
import subprocess
from typing import Union

from mloq.config import Config
from mloq.failure import Failure


def setup_git(
    path: Union[Path, str],
    project_config: Config,
    template: Config,
) -> None:
    """Initialize a Git repository over the generated files."""
    git_init = project_config["git_init"]
    if not git_init:
        return
    message = template["git_message"]
    push = project_config["git_push"]
    branch = template["default_branch"]
    project_name = template["project_name"]
    owner = template["owner"]
    sign_off = project_config["open_source"]
    path = str(path)
    try:
        _git_cmd(path, "init")
        _git_cmd(path, *f"remote add origin ssh://git@github.com/{owner}/{project_name}".split())
        _git_cmd(path, *"add .".split())
        _git_cmd(path, *f"commit {'--signoff' if sign_off else ''} -m".split(), message)
        if push:
            _git_cmd(path, *f"push origin {branch}".split())
    except subprocess.CalledProcessError as e:
        raise Failure() from e


def _git_cmd(git_dir: str, *parts: str) -> None:
    subprocess.run(("git",) + parts, check=True, cwd=git_dir)
