from pathlib import Path
import tempfile

from omegaconf import DictConfig, OmegaConf
import pytest

from mloq.files import mloq_yml, read_file
from mloq.runner import load_config


class TestLoadConfig:
    def test_load_config_empty_config(self):
        config = load_config("this_dir_does_not_exist", [])
        assert isinstance(config, DictConfig)
        example = OmegaConf.load(mloq_yml.src)
        assert config == example

    def test_load_config_file(self):
        temp_dir = tempfile.TemporaryDirectory()
        with open(Path(temp_dir.name) / mloq_yml.dst, "w") as f:
            f.write(read_file(mloq_yml))
        # Load configuration providing a directory containing an mloq.yml file
        config = load_config(temp_dir.name, [])
        assert isinstance(config, DictConfig)
        example = OmegaConf.load(mloq_yml.src)
        assert config == example
        # Load configuration providing the path to the target mloq.yml file
        config = load_config(Path(temp_dir.name) / mloq_yml.dst, [])
        assert isinstance(config, DictConfig)
        example = OmegaConf.load(mloq_yml.src)
        assert config == example
        temp_dir.cleanup()


class TestRunCommand:
    pass
