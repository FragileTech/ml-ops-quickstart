from pathlib import Path

from mloq.directories import create_github_actions_directories
from mloq.files import (
    build_pypitest_python_wkf,
    build_pypitest_source_wkf,
    build_pypitest_wheels_wkf,
    bump_version_wkf,
    docker_test_wkf,
    lint_test_wkf,
    release_package_wkf,
    release_wheels_wkf,
)
from mloq.templating import write_template


WORKFLOW_NAMES = {
    "build-python": build_pypitest_python_wkf,
    "build-source": build_pypitest_source_wkf,
    "build-wheels": build_pypitest_wheels_wkf,
    "bump-version": bump_version_wkf,
    "docker-test": docker_test_wkf,
    "lint-and-test": lint_test_wkf,
    "release-package": release_package_wkf,
    "release_wheels": release_wheels_wkf,
}


def setup_workflows(workflows, root_path: Path, params, override: bool = False):
    create_github_actions_directories(root_path)
    workflows_path = root_path / ".github" / "workflows"
    # TODO: Check for incompatible workflows
    for wkflow_name in workflows:
        workflow = WORKFLOW_NAMES.get(wkflow_name)
        if workflow is None:
            print(f"Workflow {wkflow_name} not defined. Skipping")
        else:
            write_template(workflow, params, workflows_path, override)
