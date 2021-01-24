"""This module defines the functionality to set up Github Actions workflows programmatically."""
from pathlib import Path
from typing import Union

from mloq.directories import create_github_actions_directories
from mloq.files import push_dist_wkf, push_python_wkf
from mloq.templating import write_template


WORKFLOW_NAMES = {
    "dist": push_dist_wkf,
    "python": push_python_wkf,
}


def setup_workflow_template(workflow, root_path: Path, template, override: bool = False):
    """Add the target workflows to the corresponding .github/workflows repository."""
    create_github_actions_directories(root_path)
    workflows_path = Path(root_path) / ".github" / "workflows"
    # TODO: Check for incompatible workflows
    workflow_file = WORKFLOW_NAMES.get(workflow)
    if workflow.lower() == "none":
        return
    elif workflow_file is None:
        print(f"Workflow {workflow} not defined. Skipping")
    else:
        write_template(workflow_file, params=template, path=workflows_path, override=override)


def setup_push_workflow(project_config, template, path: Union[str, Path], override: bool = False):
    """Initialize the target workflow."""
    create_github_actions_directories(path)
    wkflow = project_config.get("ci", "none")
    setup_workflow_template(workflow=wkflow, template=template, root_path=path, override=override)
