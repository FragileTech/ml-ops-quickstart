"""Command line interface for mloq."""
import os
from pathlib import Path
from typing import Callable, Optional

import click

from mloq.runner import run_command
from mloq.version import __version__


overwrite_opt = click.option(
    "--overwrite/--no-overwrite",
    "-o/ ",
    default=False,
    show_default=True,
    help="Value indicating whether to overwrite existing files.",
)
config_file_opt = click.option(
    "--filename",
    "-f",
    "config_file",
    default=None,
    show_default=True,
    help="Name of the repository config file",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
)
only_config_opt = click.option(
    "--only-config/--everything",
    "-c/ ",
    default=False,
    show_default=True,
    help="Value indicating whether to not generate all the files except mloq.yaml.",
)
output_directory_arg = click.argument(
    "output_directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
)

interactive_opt = click.option(
    "--interactive/--no-interactive",
    "-i/ ",
    default=False,
    show_default=True,
    help="If True the configuration values will be defined interactively on the command line.",
)

hydra_args = click.argument("hydra_args", nargs=-1, type=click.UNPROCESSED)


def mloq_click_command(func):
    """Wrap a command function to interface with click."""
    func = hydra_args(func)
    func = only_config_opt(func)
    func = interactive_opt(func)
    func = overwrite_opt(func)
    func = output_directory_arg(func)
    func = config_file_opt(func)
    func = click.command(context_settings=dict(ignore_unknown_options=True))(func)
    return func


class MloqCLI(click.MultiCommand):
    """Load the commands available at runtime from the files present in the command module."""

    command_folder = Path(__file__).parent / "commands"

    def list_commands(self, ctx):
        """List the names of the mloq commands available."""
        rv = []
        for filename in os.listdir(self.command_folder):
            if filename.endswith(".py") and filename != "__init__.py":
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name) -> Callable:
        """Create the command callable corresponding to the provided command name."""
        ns = {}
        fn = os.path.join(self.command_folder, name + ".py")
        with open(fn) as f:
            code = compile(f.read(), fn, "exec")
            eval(code, ns, ns)
        command_class = ns[f"{name.capitalize()}CMD"]
        # TODO: handle exit codes if needed
        return run_command(command_class)


@click.command(cls=MloqCLI)
def cli():  # noqa: D103
    pass


def welcome_message(extra: bool = False, string: Optional[str] = None):
    """Welcome message to be displayed during interactive setup."""
    click.echo(f"Welcome to the MLOQ {__version__} interactive setup utility.")
    if extra:
        click.echo(f"{string}")
    click.echo()
    click.echo(
        "Please enter values for the following settings (just press Enter "
        "to accept a default value, if one is given in brackets).",
    )
    click.echo()
