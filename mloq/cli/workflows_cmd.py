"""Implements the `mloq setup` CLI command."""
import sys

import click
from omegaconf import DictConfig

from mloq.api import workflows_project
from mloq.config.logic import write_config
from mloq.config.params import is_empty, PROJECT, TEMPLATE
from mloq.config.workflows_generation import generate_config
from mloq.failure import Failure
from mloq.files import workflows_yml
from mloq.version import __version__


def generate_config_interactive_basic(config: DictConfig) -> DictConfig:
    """Interactive generation of the project configuration."""
    # General project information
    click.echo("The following values will occur in several places in the generated files.")
    project, template = config.project, config.template
    template.project_name = TEMPLATE.project_name(template, True)
    template.owner = TEMPLATE.owner(template, True)
    template.email = TEMPLATE.email(template, True)
    template.author = TEMPLATE.author(template, True, default=template.owner)
    click.echo()
    # License information
    click.echo("Please define whether the project is Open Source")
    is_open_source = PROJECT.open_source(project, True, default=True)
    project.open_source = is_open_source
    return config


def generate_config_interactive_specific(config: DictConfig) -> DictConfig:
    """Interactive generation of the project configuration (specific module part)."""
    project, template = config.project, config.template
    default_url = f"https://github.com/{template.owner}/{template.project_name}"
    template.project_url = TEMPLATE.project_url(template, True, default=default_url)
    click.echo()
    # Continuous integration and other optional tools
    click.echo("You can configure the continuous integration using Github Actions.")
    click.echo("Available values:")
    click.echo("    Python: Push workflow for pure Python projects.")
    click.echo("    None: Do not set up the CI.")
    ci = PROJECT.ci(project, True, default="python")
    project.ci = ci
    if is_empty(ci):
        template.bot_name = "None"
        template.bot_email = "None"
    else:
        template.default_branch = TEMPLATE.default_branch(template, True, default="master")
        click.echo("A bot account will be used to automatically bump the version of your project.")
        template.bot_name = TEMPLATE.bot_name(template, True, default=template.author)
        template.bot_email = TEMPLATE.bot_email(template, True, default=template.email)

    template.ci_python_version = "3.8"
    template.ci_ubuntu_version = "ubuntu-20.04"
    template.ci_extra = ""
    project.git_init = git_init = PROJECT.git_init(project, True, default=True)
    if git_init:
        project.git_push = PROJECT.git_push(project, True, default=False)
        template.git_message = TEMPLATE.git_message(
            template,
            True,
            default="Generate project files with mloq",
        )
    return config


def welcome_message():
    """Welcome message to be displayed during interactive setup."""
    click.echo(f"Welcome to the MLOQ {__version__} interactive setup utility.")
    click.echo("This initializes a Git repository and generates GitHub workflows if requested.")
    click.echo()
    click.echo(
        "Please enter values for the following settings (just press Enter "
        "to accept a default value, if one is given in brackets).",
    )
    click.echo()


def workflows_cmd(
    config: DictConfig,
    output,
    overwrite: bool,
    interactive: bool,
    only_config: bool,
) -> int:
    """
    Initialize the project folder structure for using GitHub actions.

    Initializes the Git repository and  adds the target workflows to the
    corresponding .github/workflows repository. Moreover, it boots the
    folder structure for using GitHub actions workflows.

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
        write_config(file=workflows_yml, config=config, path=output, safe=True)
    if only_config:
        return 0
    if not overwrite and interactive:
        overwrite = click.confirm("Do you want to overwrite existing files?")
    try:
        workflows_project(
            path=output,
            config=config,
            overwrite=overwrite,
        )
    except Failure as e:
        print(f"Failed to setup the project: {e}", file=sys.stderr)
        return 1
    return 0
