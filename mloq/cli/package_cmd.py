"""Implements the `mloq setup` CLI command."""
import sys

import click
from omegaconf import DictConfig

from mloq.api import package_project
from mloq.config.logic import get_docker_image, write_config_package
from mloq.config.package_generation import generate_config
from mloq.config.params import PROJECT, TEMPLATE
from mloq.failure import Failure
from mloq.version import __version__


def generate_config_interactive(config: DictConfig) -> DictConfig:
    """Interactive generation of the project configuration."""
    # General project information
    click.echo("The following values will occur in several places in the generated files.")
    project, template = config.project, config.template
    template.project_name = TEMPLATE.project_name(template, True)
    template.description = TEMPLATE.description(template, True)
    template.owner = TEMPLATE.owner(template, True)
    template.email = TEMPLATE.email(template, True)
    template.author = TEMPLATE.author(template, True, default=template.owner)
    default_url = f"https://github.com/{template.owner}/{template.project_name}"
    template.project_url = TEMPLATE.project_url(template, True, default=default_url)
    click.echo()
    # License information
    click.echo("Please define the license of the project. ")
    click.echo(
        "Open Source projects will include the corresponding " "LICENSE file and a DCO.md file",
    )
    is_open_source = PROJECT.open_source(project, True, default=True)
    project.open_source = is_open_source
    default_license = "MIT" if is_open_source else "None"
    template.license = TEMPLATE.license(template, True, default=default_license)
    copyright_holder = TEMPLATE.copyright_holder(template, True, default=template.owner)
    template.copyright_holder = copyright_holder
    click.echo()
    # Python version and requirements
    click.echo(
        "What Python versions are supported? "
        "Please provide the values as a comma separated list. ",
    )
    versions = TEMPLATE.python_versions(template, True, default="3.6, 3.7, 3.8, 3.9")
    template.python_versions = versions
    click.echo()
    # Continuous integration and other optional tools
    template.pyproject_extra = ""
    project.docker = has_docker = PROJECT.docker(project, True, default=True)
    if has_docker:
        click.echo("MLOQ will generate a Dockerfile for your project.")
        base_docker = get_docker_image(config)
        if base_docker is not None:
            base_docker = TEMPLATE.docker_image(template, True, default=base_docker)
        template.docker_image = str(base_docker) if base_docker is None else base_docker
    click.echo("You can optionally create an ML Flow MLProject file.")
    project.mlflow = PROJECT.mlflow(project, True, default=False)
    return config


def welcome_message():
    """Welcome message to be displayed during interactive setup."""
    click.echo(f"Welcome to the MLOQ {__version__} interactive setup utility.")
    click.echo("This generates the necessary repository files for your new project.")
    click.echo()
    click.echo(
        "Please enter values for the following settings (just press Enter "
        "to accept a default value, if one is given in brackets).",
    )
    click.echo()


def package_cmd(
    config: DictConfig,
    output,
    overwrite: bool,
    interactive: bool,
    only_config: bool,
) -> int:
    """Initialize a new project using ML Ops Quickstart."""
    if interactive:
        welcome_message()
        config = generate_config_interactive(config)
    else:
        config = generate_config(config)
    if interactive and (only_config or click.confirm("Do you want to generate a mloq.yml file?")):
        write_config_package(config, output, safe=True)
    if only_config:
        return 0
    if not overwrite and interactive:
        overwrite = click.confirm("Do you want to overwrite existing files?")
    try:
        package_project(
            path=output,
            config=config,
            overwrite=overwrite,
        )
    except Failure as e:
        print(f"Failed to setup the project: {e}", file=sys.stderr)
        return 1
    return 0
