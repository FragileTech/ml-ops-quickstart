"""This module defines the functionality to set up Github Actions workflows programmatically."""
from pathlib import Path
from typing import Union

from omegaconf import DictConfig

from mloq import _logger
from mloq.config.params import is_empty
from mloq.files import Ledger, push_python_wkf
from mloq.skeleton import create_github_actions_directories
from mloq.templating import write_template


WORKFLOW_NAMES = {
    "python": push_python_wkf,
}


def setup_workflow_template(
    root_path: Union[Path, str],
    config: DictConfig,
    ledger: Ledger,
    overwrite: bool = False,
):
    """Add the target workflows to the corresponding .github/workflows repository."""
    workflow = config.project.get("ci", "empty")
    if is_empty(workflow):
        return
    root_path = Path(root_path)
    create_github_actions_directories(root_path)
    workflows_path = Path(root_path) / ".github" / "workflows"
    workflow_file = WORKFLOW_NAMES.get(workflow)
    if workflow_file is None:
        _logger.warning(f"Workflow {workflow} not defined. Skipping")
    else:
        write_template(
            workflow_file,
            config=config,
            path=workflows_path,
            ledger=ledger,
            overwrite=overwrite,
        )


def setup_push_workflow(
    path: Union[str, Path],
    config: DictConfig,
    ledger: Ledger,
    overwrite: bool = False,
) -> None:
    """Initialize the target workflow."""
    if is_empty(config.project.get("ci", "empty")):
        return
    create_github_actions_directories(path)
    setup_workflow_template(
        config=config,
        root_path=path,
        ledger=ledger,
        overwrite=overwrite,
    )
