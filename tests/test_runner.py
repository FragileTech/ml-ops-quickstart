import filecmp
import os
import os.path
from pathlib import Path
import shutil
import tempfile

from omegaconf import DictConfig, OmegaConf
import pytest

from mloq.commands import CiCMD, DockerCMD, DocsCMD, LicenseCMD, LintCMD, ProjectCMD, SetupCMD
from mloq.files import mloq_yml, read_file
from mloq.runner import load_config, run_command


COMMANDS = [CiCMD, DockerCMD, DocsCMD, SetupCMD]  # [ProjectCMD, LintCMD, LicenseCMD, SetupCMD]

CMD_CLASS_TO_NAME = {
    CiCMD: "ci",
    DockerCMD: "docker",
    DocsCMD: "docs",
    SetupCMD: "setup",
    ProjectCMD: "project",
    LintCMD: "lint",
    LicenseCMD: "license",
}


def generate_command_examples(commands):
    examples = []
    docs_test_examples = Path(__file__).parent / "examples"
    for cmd in commands:
        for example in os.listdir(docs_test_examples / CMD_CLASS_TO_NAME[cmd]):
            examples.append((cmd, docs_test_examples / CMD_CLASS_TO_NAME[cmd] / example))
    return examples


def id_func(example):
    command, folder = example
    return f"{command.cmd_name}-{folder.name}"


@pytest.fixture(scope="function", params=generate_command_examples(COMMANDS), ids=id_func)
def command_example(request):
    return request.param


def dir_trees_are_equal(dir1, dir2):
    """
    Compare two directories recursively. Files in each directory are
    assumed to be equal if their names and contents are equal.

    @param dir1: First directory path
    @param dir2: Second directory path

    @return: True if the directory trees are the same and
        there were no errors while accessing the directories or files,
        False otherwise.
    """

    dirs_cmp = filecmp.dircmp(dir1, dir2)
    if (
        len(dirs_cmp.left_only) > 0
        or len(dirs_cmp.right_only) > 0
        or len(dirs_cmp.funny_files) > 0
    ):
        return False
    (_, mismatch, errors) = filecmp.cmpfiles(dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch) > 0 or len(errors) > 0:
        return False
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if not dir_trees_are_equal(new_dir1, new_dir2):
            return False
    return True


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
        # Load configuration providing a directory containing an mloq.yaml file
        config = load_config(temp_dir.name, [])
        assert isinstance(config, DictConfig)
        example = OmegaConf.load(mloq_yml.src)
        assert config == example
        # Load configuration providing the path to the target mloq.yaml file
        config = load_config(Path(temp_dir.name) / mloq_yml.dst, [])
        assert isinstance(config, DictConfig)
        example = OmegaConf.load(mloq_yml.src)
        assert config == example
        temp_dir.cleanup()


class TestRunCommand:
    def test_run_command(self, command_example):
        if command_example is None:
            return
        cls, example_dir = command_example
        _run_cmd = run_command(cls, use_click=False)
        config_file = Path(example_dir) / mloq_yml.dst
        target_example_path = Path(example_dir) / "target"
        temp_dir = tempfile.TemporaryDirectory()
        target_path = Path(temp_dir.name) / "target"
        os.makedirs(target_path)
        _run_cmd(
            config_file=config_file,
            output_directory=target_path,
            overwrite=False,
            only_config=False,
            interactive=False,
            hydra_args="",
        )

        # The setup command create a test folder and a Makefile that interfere with make test.
        # Let's remove them so the project does not crash.
        if cls == SetupCMD:
            shutil.rmtree(target_path / "tests")
            os.remove(target_path / "Makefile")
        assert (
            dir_trees_are_equal(str(target_example_path), str(target_path)),
            set(os.listdir(target_path)) - set(os.listdir(target_example_path)),
        )
        temp_dir.cleanup()
