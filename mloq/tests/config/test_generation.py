import click
from click.testing import CliRunner
import pytest

from mloq.config.generation import generate_template


def test_generate_template():
    @click.command()
    def command(*args, **kwargs):
        return generate_template(interactive=True)

    CliRunner(echo_stdin=True).invoke(command)
