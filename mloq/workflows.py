"""This module defines the functionality to set up Github Actions workflows programmatically."""
from pathlib import Path
from typing import Union

from mloq import _logger
from mloq.config.params import Config, is_empty
from mloq.directories import create_github_actions_directories
from mloq.files import push_dist_wkf, push_python_wkf
from mloq.templating import write_template


WORKFLOW_NAMES = {
    "dist": push_dist_wkf,
    "python": push_python_wkf,
}


def setup_workflow_template(
    root_path: Union[Path, str],
    project_config: Config,
    template: Config,
    override: bool = False,
):
    """Add the target workflows to the corresponding .github/workflows repository."""
    workflow = project_config.get("ci", "empty")
    if is_empty(workflow):
        return
    root_path = Path(root_path)
    create_github_actions_directories(root_path)
    workflows_path = Path(root_path) / ".github" / "workflows"
    # TODO: Check for incompatible workflows
    workflow_file = WORKFLOW_NAMES.get(workflow)
    if workflow_file is None:
        _logger.warning(f"Workflow {workflow} not defined. Skipping")
    else:
        write_template(workflow_file, template=template, path=workflows_path, override=override)


def setup_push_workflow(
    path: Union[str, Path],
    project_config: Config,
    template: Config,
    override: bool = False,
) -> None:
    """Initialize the target workflow."""
    if is_empty(project_config.get("ci", "empty")):
        return
    create_github_actions_directories(path)
    setup_workflow_template(
        project_config=project_config,
        template=template,
        root_path=path,
        override=override,
    )
