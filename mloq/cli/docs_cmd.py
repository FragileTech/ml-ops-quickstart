"""Implements the `mloq setup` CLI command."""
import sys

import click
from omegaconf import DictConfig

from mloq.api import docs_project
from mloq.config.docs_generation import generate_config
from mloq.config.logic import write_config_docs
from mloq.config.params import TEMPLATE
from mloq.failure import Failure
from mloq.version import __version__


def generate_config_interactive(config: DictConfig) -> DictConfig:
    """Interactive generation of the project configuration."""
    # General project information
    click.echo("The following values will occur in several places in the generated files.")
    project, template = config.project, config.template
    template.project_name = TEMPLATE.project_name(template, True)
    template.description = TEMPLATE.description(template, True)
    template.author = TEMPLATE.author(template, True)
    click.echo()
    copyright_holder = TEMPLATE.copyright_holder(template, True, default=template.author)
    template.copyright_holder = copyright_holder
    click.echo()
    # Python version and requirements
    project.docs = True
    return config


def welcome_message():
    """Welcome message to be displayed during interactive documentation setup."""
    click.echo(f"Welcome to the MLOQ {__version__} interactive setup utility.")
    click.echo("This generates the necessary documentation for your new project.")
    click.echo()
    click.echo(
        "Please enter values for the following settings (just press Enter "
        "to accept a default value, if one is given in brackets).",
    )
    click.echo()


def docs_cmd(
    config: DictConfig,
    output,
    overwrite: bool,
    interactive: bool,
    only_config: bool,
) -> int:
    """
    Initialize the documentation of a new project using ML Ops Quickstart.

    Create the necessary documentation files of the new project (following
    ML Ops best practices).

    Args:
        config: Configuration Dictionary including the defined parameters.
        output: TODO
        overwrite: If True, overwrites the existent `mloq.yml` file.
        interactive: If True, activates the interactive mode to request
            the configuration inputs.
        only_config: TODO

    Returns:
        Returns an integer value indicating whether the process has
            ended successfully.
    """
    if interactive:
        welcome_message()
        config = generate_config_interactive(config)
    else:
        config = generate_config(config)
    if interactive and (only_config or click.confirm("Do you want to generate a mloq.yml file?")):
        write_config_docs(config, output, safe=True)
    if only_config:
        return 0
    if not overwrite and interactive:
        overwrite = click.confirm("Do you want to overwrite existing files?")
    try:
        docs_project(
            path=output,
            config=config,
            overwrite=overwrite,
        )
    except Failure as e:
        print(f"Failed to setup the project: {e}", file=sys.stderr)
        return 1
    return 0
