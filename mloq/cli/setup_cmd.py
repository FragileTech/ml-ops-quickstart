"""Implements the `mloq setup` CLI command."""
import sys
from typing import Tuple

import click
from omegaconf import DictConfig

from mloq.api import setup_modules, setup_project
from mloq.cli.docs_cmd import generate_config_interactive_specific as spec_docs
from mloq.cli.package_cmd import generate_config_interactive_specific as spec_package
from mloq.cli.requirements_cmd import generate_config_interactive_specific as spec_requir
from mloq.cli.workflows_cmd import generate_config_interactive_specific as spec_gitwork
from mloq.config.logic import get_docker_image, write_config
from mloq.config.params import is_empty, PROJECT, TEMPLATE
from mloq.config.setup_generation import generate_config
from mloq.failure import Failure
from mloq.files import setup_yml
from mloq.version import __version__


def super_config_interactive(config: DictConfig) -> Tuple[DictConfig, bool]:
    """
    Generate the project configuration.

    This method starts the interactive configuration process of the project.
    Depending on the input, it will call a generative function that will
    fill out the template according to the interactive entries.

    Args:
        config: DictConfig containing the selected project configuration.

    Return:
        It returns a DictConfig object (with values assigned by the user)
            that will be used as basis to generate the project files.
    """
    complete = PROJECT.complete(config.project, True, default=True)
    if complete:
        config = generate_config_interactive(config)
    else:
        config = generate_module_interactive(config)
    return config, complete


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
    template.pyproject_extra = ""
    template.docstring_checks = False
    project.docker = has_docker = PROJECT.docker(project, True, default=True)
    if has_docker:
        click.echo("MLOQ will generate a Dockerfile for your project.")
        base_docker = get_docker_image(config)
        if base_docker is not None:
            base_docker = TEMPLATE.docker_image(template, True, default=base_docker)
        template.docker_image = str(base_docker) if base_docker is None else base_docker
    project.docs = PROJECT.docs(project, True, default=True)
    click.echo("You can optionally create an ML Flow MLProject file.")
    project.mlflow = PROJECT.mlflow(project, True, default=False)
    project.git_init = git_init = PROJECT.git_init(project, True, default=True)
    if git_init:
        project.git_push = PROJECT.git_push(project, True, default=False)
        template.git_message = TEMPLATE.git_message(
            template,
            True,
            default="Generate project files with mloq",
        )
    return config


def generate_module_interactive(config: DictConfig) -> DictConfig:
    """
    Interactive generation of the project configuration.

    Depending on which modules are selected, it writes interactively the
    configuration of the project. Only the entries related to the selected
    modules will be completed.
    """
    project, template = config.project, config.template
    # Selection modules
    click.echo()
    click.echo(
        "Which modules do you want to install? Please, select the values as a comma separated "
        "list.",
    )
    click.echo("Available values:")
    click.echo(
        "    project_files: initialize root folder files and generate common repository files.",
    )
    click.echo("    docs: configure the documentation of the project.")
    click.echo("    requirements: write requirements files.")
    click.echo(
        "    git_workflows: initialize initialize a Git repository over the generated "
        "files, and set up the project for using GitHub actions workflows.",
    )
    project.modules = PROJECT.modules(project, True, default="project_files")
    package = "project_files" in project.modules
    docs = "docs" in project.modules
    git_workflows = "git_workflows" in project.modules
    requirements = "requirements" in project.modules
    # Basic config
    click.echo("The following values will occur in several places in the generated files.")
    template.project_name = TEMPLATE.project_name(template, True)
    template.description = TEMPLATE.description(template, True)
    template.owner = TEMPLATE.owner(template, True)
    template.email = TEMPLATE.email(template, True)
    template.author = TEMPLATE.author(template, True, default=template.owner)
    copyright_holder = TEMPLATE.copyright_holder(template, True, default=template.owner)
    template.copyright_holder = copyright_holder
    click.echo()
    # License information
    click.echo("Please define the nature of the project. ")
    click.echo(
        "Open Source projects will include the corresponding " "LICENSE file and a DCO.md file",
    )
    is_open_source = PROJECT.open_source(project, True, default=True)
    project.open_source = is_open_source
    # Specific configurations
    if package:
        spec_package(config)
    if docs:
        spec_docs(config)
    if requirements:
        spec_requir(config)
    if git_workflows:
        spec_gitwork(config)
    return config


def welcome_message():
    """Welcome message to be displayed during interactive setup."""
    click.echo(f"Welcome to the MLOQ {__version__} interactive setup utility.")
    click.echo()
    click.echo(
        "Please enter values for the following settings (just press Enter "
        "to accept a default value, if one is given in brackets).",
    )
    click.echo()


def setup_cmd(
    config: DictConfig,
    output,
    overwrite: bool,
    interactive: bool,
    only_config: bool,
) -> int:
    """Initialize a new project using ML Ops Quickstart."""
    complete = True  # Assume that user wants full installation
    if interactive:
        welcome_message()
        config, complete = super_config_interactive(config)
    else:
        config = generate_config(config)
    if interactive and (only_config or click.confirm("Do you want to generate a mloq.yml file?")):
        write_config(setup_yml, config, output, safe=True)
    if only_config:
        return 0
    if not overwrite and interactive:
        overwrite = click.confirm("Do you want to overwrite existing files?")
    if complete:
        try:
            setup_project(
                path=output,
                config=config,
                overwrite=overwrite,
            )
        except Failure as e:
            print(f"Failed to setup the project: {e}", file=sys.stderr)
            return 1
        return 0
    elif not complete:
        try:
            setup_modules(
                path=output,
                config=config,
                overwrite=overwrite,
            )
        except Failure as e:
            print(f"Failed to setup the project: {e}", file=sys.stderr)
            return 1
        return 0
