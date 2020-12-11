from pathlib import Path

from mltemplate.directories import create_github_actions_directories
from mltemplate.files import bump_version_wkf, docker_test_wkf, lint_test_wkf
from mltemplate.templating import write_template


def setup_workflows(workflows, root_path: Path, params, override: bool = False):
    create_github_actions_directories(root_path)
    workflows_path = root_path / ".github" / "workflows"
    if "lint-and-test" in workflows:
        write_template(lint_test_wkf, params, workflows_path, override)
    if "bump-version" in workflows:
        write_template(bump_version_wkf, params, workflows_path, override)
    if "docker-test" in workflows:
        write_template(docker_test_wkf, params, workflows_path, override)
