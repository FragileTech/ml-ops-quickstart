"""Implements the `mloq setup` CLI command."""
import sys

import click
from omegaconf import DictConfig

from mloq.api import requirement_project
from mloq.config.logic import write_config
from mloq.config.params import PROJECT
from mloq.config.requirements_generation import generate_config
from mloq.failure import Failure
from mloq.files import requirements_yml
from mloq.version import __version__


def generate_config_interactive_basic(config: DictConfig) -> DictConfig:
    """Interactive generation of the project configuration."""
    # General project information
    return config


def generate_config_interactive_specific(config: DictConfig) -> DictConfig:
    """Interactive generation of the project configuration (specific module part)."""
    project, template = config.project, config.template
    click.echo()
    click.echo("Please specify the requirements of the project as a comma separated list.")
    click.echo("Available values:")
    click.echo("    data-science: Common data science libraries such as numpy, pandas, sklearn...")
    click.echo(
        "    data-viz: Visualization libraries such as holoviews, bokeh, plotly, matplotlib...",
    )
    click.echo("    pytorch: Latest version of pytorch, torchvision and pytorch_lightning")
    click.echo("    tensorflow: ")  # , data-viz, torch, tensorflow}")
    project_requirements = PROJECT.requirements(project, True, default="None")
    project.requirements = project_requirements
    template.docstring_checks = False
    return config


def welcome_message():
    """Welcome message to be displayed during interactive requirement setup."""
    click.echo(f"Welcome to the MLOQ {__version__} interactive setup utility.")
    click.echo("This generates the necessary requirement files for your new project.")
    click.echo()
    click.echo(
        "Please enter values for the following settings (just press Enter "
        "to accept a default value, if one is given in brackets).",
    )
    click.echo()


def requirements_cmd(
    config: DictConfig,
    output,
    overwrite: bool,
    interactive: bool,
    only_config: bool,
) -> int:
    """
    Initialize the requirement files of a new project using ML Ops Quickstart.

    Create requirement files according to the options selected by the user.
    Requirement files are grouped into 7 different categories based on
    the needs they cover:
    - data-science
    - data-visualization
    - pytorch
    - tensorflow
    - documentation requirements
    - linter requirements
    - test requirements

    Args:
        config: DictConfig containing the selected project configuration.
        output: Target folder where the files will be written.
        overwrite: If True, overwrites the existent `mloq.yml` file.
        interactive: If True, activates the interactive mode to request
            the configuration inputs.
        only_config: TODO
    Returns:
        It returns an integer value showing whether the process has ended
            successfully.
    """
    if interactive:
        welcome_message()
        config = generate_config_interactive_basic(config)
        config = generate_config_interactive_specific(config)
    else:
        config = generate_config(config)
    if interactive and (only_config or click.confirm("Do you want to generate a mloq.yml file?")):
        write_config(requirements_yml, config, output, safe=True)
    if only_config:
        return 0
    if not overwrite and interactive:
        overwrite = click.confirm("Do you want to overwrite existing files?")
    try:
        requirement_project(
            path=output,
            config=config,
            overwrite=overwrite,
        )
    except Failure as e:
        print(f"Failed to setup the project: {e}", file=sys.stderr)
        return 1
    return 0
