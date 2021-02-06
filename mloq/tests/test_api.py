from pathlib import Path
import tempfile

import invoke
import pytest

from mloq.api import setup_project, setup_requirements
from mloq.files import test_req


@pytest.fixture()
def repo_path():
    return Path(__file__).parent / "test_project"


def test_init_repository(project_config, template):
    with tempfile.TemporaryDirectory() as tmp:
        setup_project(
            path=Path(tmp),
            project_config=project_config,
            template=template,
            override=False,
        )


def test_setup_requirements():
    try:
        setup_requirements(test_req.src.parent, project_config={}, install=("all",))
    except invoke.exceptions.UnexpectedExit:
        pass
    setup_requirements(test_req.src.parent, project_config={}, install=("lint",))
