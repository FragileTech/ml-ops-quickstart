from pathlib import Path
import tempfile

import invoke

from mloq.api import setup_project, setup_requirements
from mloq.files import test_req


def test_init_repository(project_config, template):
    with tempfile.TemporaryDirectory() as tmp:
        setup_project(
            path=Path(tmp),
            project_config=project_config,
            template=template,
            override=False,
        )


def test_setup_requirements(ledger):
    try:
        setup_requirements(test_req.src.parent, project_config={}, install=("all",), ledger=ledger)
    except invoke.exceptions.UnexpectedExit:
        pass
    setup_requirements(test_req.src.parent, project_config={}, install=("lint",), ledger=ledger)
