from pathlib import Path
import tempfile

from mloq.config.logic import write_config


def test_write_config(mloq_yaml_dict):
    with tempfile.TemporaryDirectory() as tmp:
        write_config(mloq_yaml_dict, path=Path(tmp) / "_mloq.yml")
