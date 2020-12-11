from pathlib import Path
import tempfile

import pytest

from mloq.api import init_repository


@pytest.fixture()
def repo_path():
    return Path(__file__).parent / "test_project"


def test_init_repository(repo_path):
    with tempfile.TemporaryDirectory() as tmp:
        init_repository(
            Path(tmp), config_file=Path(__file__).parent / "repository.yaml", override=False
        )
