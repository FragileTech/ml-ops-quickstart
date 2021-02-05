import tempfile

from click.testing import CliRunner

from mloq.cli.main import cli
from mloq.tests.cli.cli_inputs import cli_input


def test_setup_interactive(cli_input):
    with tempfile.TemporaryDirectory() as tmp:
        runner = CliRunner(echo_stdin=True)
        result = runner.invoke(cli, ["setup", "-i", str(tmp)], input=cli_input)
    assert result.exit_code == 0, result.stdout
