from pathlib import Path
import tempfile

import invoke
from omegaconf import DictConfig

from mloq.api import setup_project, setup_requirements
from mloq.files import test_req


def test_init_repository(config):
    with tempfile.TemporaryDirectory() as tmp:
        setup_project(
            path=Path(tmp),
            config=config,
            override=False,
        )


def test_setup_requirements(ledger):
    try:
        setup_requirements(
            test_req.src.parent,
            config=DictConfig({"project": {}, "template": {}}),
            install=("all",),
            ledger=ledger,
        )
    except invoke.exceptions.UnexpectedExit:
        pass
    setup_requirements(
        test_req.src.parent,
        config=DictConfig({"project": {}, "template": {}}),
        install=("lint",),
        ledger=ledger,
    )
