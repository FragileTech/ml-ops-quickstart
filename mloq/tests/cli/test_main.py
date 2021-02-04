import tempfile

from click.testing import CliRunner

from mloq.cli.main import cli


def test_setup_interactive():
    cli_input = (
        "test_project_name\n"  # Project name
        "my_test_description\n"  # Description
        "owner\n"  # project owner
        "owner@email.com\n"
        "\n"  # Authors, set to owner
        "\n"  # url default
        "\n"  # open source
        "\n"  # Mit license
        "Owner LTD\n"  # copyright owner
        "\n"  # Python versions
        "torch\n"  # requirements
        "\n"  # Workflow python
        "\n"  # default branch master
        "bot-account\n"  # bot
        "bot@email.com\n"  # bot email
        "\n"  # Default base docker image
        "\n"  # No ML Flow
        "\n"  # Init git repo
        "\n"  # No push
        "\n"  # Default commit message
        "y\n"  # Generate mloq.yml
        "y\n"  # Overwrite files
    )

    with tempfile.TemporaryDirectory() as tmp:
        runner = CliRunner(echo_stdin=True)
        result = runner.invoke(cli, ["setup", "-i", str(tmp)], input=cli_input)
    assert result.exit_code == 0
