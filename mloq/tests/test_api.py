from pathlib import Path
import tempfile

import pytest

from mloq.api import setup_repository


@pytest.fixture()
def repo_path():
    return Path(__file__).parent / "test_project"


def test_init_repository(repo_path):
    with tempfile.TemporaryDirectory() as tmp:
        setup_repository(Path(tmp), config_file=Path(__file__).parent / "mloq.yml", override=False)
