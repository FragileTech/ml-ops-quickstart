"""Command line interface for mloq."""
from pathlib import Path

import click

from mloq.api import (
    init_config as _init_config,
    requirements as _requirements,
    setup_project_files,
    setup_push_workflow,
    setup_repository,
)
from mloq.configuration.config_values import MLOQFile
from mloq.configuration.core import set_docker_image


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
    default=None,
    show_default=True,
    help="Name of the repository config file",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
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
    default="mloq.yml",
    show_default=True,
    help="Name of the generated config file",
)
def init_config(override, filename, output):  # noqa
    """
    Initialize a new config file.

    Parameters:

        OUTPUT: Path where the new mloq.yml template will be written.
    """
    filename = filename if filename != "mloq.yml" else None
    _init_config(output, override, filename)
    click.echo(f"Created new repository config at {Path(output) / filename}")


@cli.command()
@override_opt
@output_path_arg
@config_file_opt
def setup(override, config_file, output):  # noqa
    """
    Set up a new project.

    Parameters:

        OUTPUT: Path where the new mloq.yml template will be written.
    """
    setup_repository(path=output, config_file=config_file, override=override)


@cli.command()
@override_opt
@output_path_arg
@config_file_opt
@click.option(
    "--push",
    "-p",
    type=click.Choice(["python", "dist"], case_sensitive=False),
    help="python creates a workflow for pure python projects | dist creates a workflow "
    "for projects that contain non-python extensions.",
)
def workflows(override, config_file, output, push):  # noqa
    """
    Set up GitHub Actions CI workflow.

    Set up the Github Actions workflow containing the CI pipeline \
    triggered on push and pull request events.

    Parameters:

        OUTPUT: Path where the new mloq.yml template will be written.
    """
    setup_push_workflow(workflow=push, override=override, path=output, config_file=config_file)


@cli.command()
@override_opt
@output_path_arg
@config_file_opt
@click.option("--write", "-w", multiple=True, default=["all"])
@click.option("--opt", "options", multiple=True, default=[None])
@click.option("--install", "-i", multiple=True, default=[None])
def requirements(override, output, config_file, options, write, install):  # noqa
    """
    Write the project requirements files.

    Parameters:

        OUTPUT: Path where the new mloq.yml template will be written.
    """
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


@cli.command()
@override_opt
@output_path_arg
@config_file_opt
def project_files(config_file, output, override):  # noqa
    """
    Create common project config files.

    project-files creates the following configuration files filled with the target template values:

    \b
    - README.md
    - DCO.md
    - code_of_conduct.md
    - pyproject.toml
    - setup.py
    - LICENSE
    - Dockerfile
    - MLproject
    - Makefile

    Parameters:

        OUTPUT: Path of the project where the template files will be written.
    """
    setup_project_files(path=output, template=config_file, override=override)


@MLOQFile.click_command(cli, override_opt, output_path_arg)
def quickstart(output, override, **kwargs):  # noqa
    """
    Interactive initialization of a new project.

    Parameters:

        OUTPUT: Path of the project where the template files will be written.
    """
    MLOQFile.set_target(output)
    MLOQFile.save_config(kwargs, from_kwargs=True)
    config = MLOQFile.to_config(**kwargs)
    config = set_docker_image(config)
    setup_repository(path=output, config_file=config, override=override)
