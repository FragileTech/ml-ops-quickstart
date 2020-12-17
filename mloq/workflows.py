"""This module defines the functionality to set up Github Actions workflows programmatically."""
from pathlib import Path

from mloq.directories import create_github_actions_directories
from mloq.files import push_dist_wkf, push_python_wkf
from mloq.templating import write_template


WORKFLOW_NAMES = {
    "push-dist": push_dist_wkf,
    "push-python": push_python_wkf,
}


def setup_workflows(workflows, root_path: Path, params, override: bool = False):
    """Add the target workflows to the corresponding .github/workflows repository."""
    create_github_actions_directories(root_path)
    workflows_path = root_path / ".github" / "workflows"
    # TODO: Check for incompatible workflows
    for wkflow_name in workflows:
        workflow = WORKFLOW_NAMES.get(wkflow_name)
        if workflow is None:
            print(f"Workflow {wkflow_name} not defined. Skipping")
        else:
            write_template(workflow, params, workflows_path, override)
