from pathlib import Path
import tempfile

import pytest

from mloq.api import setup_project


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
