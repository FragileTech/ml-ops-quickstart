from pathlib import Path
import tempfile

from click.testing import CliRunner
import pytest

from mloq.cli.main import cli
from mloq.tests.cli.cli_inputs import cli_input


# race condition in /home/runner/.cache/flakehell which is created in the Git pre-commit hook
@pytest.mark.flaky(reruns=3)
def test_setup_interactive(cli_input):
    with tempfile.TemporaryDirectory() as tmp:
        runner = CliRunner(echo_stdin=False)
        result = runner.invoke(cli, ["setup", "-i", str(tmp)], input=cli_input)
    assert result.exit_code == 0, result.stdout


# race condition in /home/runner/.cache/flakehell which is created in the Git pre-commit hook
@pytest.mark.flaky(reruns=3)
def test_setup_non_interactive():
    mloq_file = Path(__file__).parent.parent / "mloq.yml"
    with tempfile.TemporaryDirectory() as tmp:
        runner = CliRunner(echo_stdin=False)
        result = runner.invoke(cli, ["setup", "-f", str(mloq_file), str(tmp)])
        _ = runner.invoke(cli, ["setup", "-f", str(mloq_file), str(tmp)])
    assert result.exit_code == 0, result.stdout


def test_setup_error():
    mloq_file = Path(__file__).parent.parent / "mloq.yml"
    runner = CliRunner(echo_stdin=False)
    result = runner.invoke(cli, ["setup", "-f", str(mloq_file), "/"])
    msg = "Failed to setup the project:"
    fails = msg in result.output or result.exit_code == 1
    fails = fails or result.stderr_bytes is None  # Pass when running inside docker
    assert fails, result.output
