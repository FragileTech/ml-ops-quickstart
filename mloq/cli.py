from pathlib import Path

import click

from mloq.api import (
    init_config as _init_config,
    requirements as _requirements,
    setup_repository,
    setup_workflow,
)


override_opt = click.option(
    "--override/--no-override",
    "-o/ ",
    default=False,
    show_default=True,
    help="If True overwrite existing files. If False ignore files that already exist.",
)
config_file_opt = click.option(
    "--filename",
    "-f",
    "config_file",
    default="repository.yml",
    show_default=True,
    help="Name of the repository config file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
)


output_path_arg = click.argument(
    "output", type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True)
)


@click.group()
def cli():
    pass


@cli.command()
@output_path_arg
@override_opt
@click.option(
    "--filename",
    "-f",
    "filename",
    default="repository.yml",
    show_default=True,
    help="Name of the generated config file",
)
def init_config(override, filename, output):
    """
    Initialize a new config file.

    Parameters:

        OUTPUT: Path where the new repository.yml template will be written.
    """
    filename = filename if filename != "repository.yml" else None
    _init_config(output, override, filename)
    click.echo(f"Created new repository config at {Path(output) / filename}")


@cli.command()
@override_opt
@output_path_arg
@config_file_opt
def setup(override, config_file, output):
    """
    Set up a new project.

    Parameters:

        OUTPUT: Path where the new repository.yml template will be written.
    """
    setup_repository(path=output, config_file=config_file, override=override)


@cli.command()
@override_opt
@output_path_arg
@config_file_opt
@click.option("--push", "-p", type=click.Choice(["python", "dist"], case_sensitive=False))
def workflows(override, config_file, output, push):
    setup_workflow(
        workflow=f"push-{push}", override=override, path=output, config_file=config_file
    )


@cli.command()
@override_opt
@output_path_arg
@config_file_opt
@click.option("--write", "-w", multiple=True, default=["all"])
@click.option("--opt", "options", multiple=True, default=[None])
@click.option("--install", "-i", multiple=True, default=[None])
def requirements(override, output, config_file, options, write, install):
    if "all" in write:
        dev, lint = True, True
    else:
        dev = "test" in write
        lint = "lint" in write

    options = config_file if options[0] is None else options
    install = install if install[0] is not None else None
    _requirements(
        options=options, override=override, path=output, install=install, test=dev, lint=lint
    )
