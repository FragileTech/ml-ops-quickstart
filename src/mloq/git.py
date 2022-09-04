"""Setup Git repository for the project."""


from pathlib import Path
import subprocess
from typing import Union

from omegaconf import DictConfig

from mloq.failure import Failure


def setup_git(
    path: Union[Path, str],
    config: DictConfig,
) -> None:
    """Initialize a Git repository over the generated files."""
    git_init = config.project.git_init
    if not git_init:
        return
    message = config.template.git_message
    push = config.project.git_push
    branch = config.template.default_branch
    project_name = config.template.project_name
    owner = config.template.owner
    sign_off = config.project.open_source
    path = str(path)
    try:
        _git_cmd(path, "init")
        _git_cmd(path, *f"remote add origin ssh://git@github.com/{owner}/{project_name}".split())
        subprocess.run(("pre-commit", "install"), check=True, cwd=path)

        def commit_all():
            _git_cmd(path, *"add .".split())
            _git_cmd(path, *f"commit {'--signoff' if sign_off else ''} -m".split(), message)

        if push:
            _git_cmd(path, *f"checkout -b {branch}".split())
            _git_cmd(path, *"add README.md".split())
            _git_cmd(
                path,
                *f"commit {'--signoff' if sign_off else ''} -m".split(),
                f"Initialize {branch}",
            )
            _git_cmd(path, *f"push origin {branch}".split())

        commit_all()

        if push:
            _git_cmd(path, *f"push origin HEAD:init-{branch}".split())
    except subprocess.CalledProcessError as e:
        raise Failure() from e


def _git_cmd(git_dir: str, *parts: str) -> None:
    subprocess.run(("git",) + parts, check=True, cwd=git_dir)
