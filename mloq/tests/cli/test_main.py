from pathlib import Path
import tempfile

from click.testing import CliRunner

from mloq.cli.main import cli
from mloq.tests.cli.cli_inputs import cli_input


def test_setup_interactive(cli_input):
    with tempfile.TemporaryDirectory() as tmp:
        runner = CliRunner(echo_stdin=False)
        result = runner.invoke(cli, ["setup", "-i", str(tmp)], input=cli_input)
    assert result.exit_code == 0, result.stdout


def test_setup_non_interactive():
    mloq_file = Path(__file__).parent.parent / "mloq.yml"
    with tempfile.TemporaryDirectory() as tmp:
        runner = CliRunner(echo_stdin=False)
        result = runner.invoke(cli, ["setup", "-f", str(mloq_file), str(tmp)])
        result = runner.invoke(cli, ["setup", "-f", str(mloq_file), str(tmp)])
    assert result.exit_code == 0, result.stdout
