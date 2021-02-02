"""Implements the `mloq setup` CLI command."""
import sys

import click

from mloq.api import setup_project
from mloq.config.generation import generate_project_config, generate_template
from mloq.config.logic import get_docker_image, read_config_safe, write_config
from mloq.config.params import Config, is_empty, PROJECT_CONFIG, TEMPLATE
from mloq.failure import Failure
from mloq.version import __version__


def generate_config_interactive(template: Config, project_config: Config):
    """Interactive generation of the project configuration."""
    # General project information
    click.echo("The following values will occur in several places in the generated files.")
    template["project_name"] = TEMPLATE["project_name"](template, True)
    template["description"] = TEMPLATE["description"](template, True)
    template["owner"] = TEMPLATE["owner"](template, True)
    template["email"] = TEMPLATE["email"](template, True)
    template["author"] = TEMPLATE["author"](template, True, default=template["owner"])
    default_url = f"https://github.com/{template['owner']}/{template['project_name']}"
    template["project_url"] = TEMPLATE["project_url"](template, True, default=default_url)
    click.echo()
    # License information
    click.echo("Please define the license of the project. ")
    click.echo(
        "Open Source projects will include the corresponding " "LICENSE file and a DCO.md file",
    )
    is_open_source = PROJECT_CONFIG["open_source"](project_config, True, default=True)
    project_config["open_source"] = is_open_source
    default_license = "MIT" if is_open_source else "proprietary"
    template["license"] = TEMPLATE["license_type"](template, True, default=default_license)
    copyright_holder = TEMPLATE["copyright_holder"](template, True, default=template["owner"])
    template["copyright_holder"] = copyright_holder
    click.echo()
    # Python version and requirements
    click.echo(
        "What Python versions are supported? "
        "Please provide the values as a comma separated list. ",
    )
    versions = TEMPLATE["python_versions"](template, True, default="3.6, 3.7, 3.8, 3.9")
    template["python_versions"] = versions
    click.echo("Please specify the requirements of the project as a comma separated list.")
    click.echo("Available values:")
    click.echo("    data-science: Common data science libraries such as numpy, pandas, sklearn...")
    click.echo(
        "    data-viz: Visualization libraries such as holoviews, bokeh, plotly, matplotlib...",
    )
    click.echo("    pytorch: Latest version of pytorch, torchvision and pytorch_lightning")
    click.echo("    tensorflow: ")  # , data-viz, torch, tensorflow}")
    project_requirements = PROJECT_CONFIG["requirements"](project_config, True, default="None")
    project_config["requirements"] = project_requirements
    click.echo()
    # Continuous integration and other optional tools
    click.echo("You can configure the continuous integration using Github Actions.")
    click.echo("Available values:")
    click.echo("    Python: Push workflow for pure Python projects.")
    click.echo("    Dist: Push workflow for Python projects with compiled extensions.")
    click.echo("    None: Do not set up the CI.")
    ci = PROJECT_CONFIG["ci"](project_config, True, default="python")
    project_config["ci"] = ci
    if is_empty(ci):
        template["bot_name"] = "None"
        template["bot_email"] = "None"
    else:
        template["default_branch"] = TEMPLATE["default_branch"](template, True, default="master")
        click.echo("A bot account will be used to automatically bump the version of your project.")
        template["bot_name"] = TEMPLATE["bot_name"](template, True, default=template["author"])
        template["bot_email"] = TEMPLATE["bot_email"](template, True, default=template["email"])

    project_config["docker"] = True
    click.echo("MLOQ will generate a Dockerfile for your project.")
    base_docker = get_docker_image(template=template, project_config=project_config)
    if base_docker is not None:
        base_docker = TEMPLATE["docker_image"](template, True, default=base_docker)
    template["docker_image"] = str(base_docker) if base_docker is None else base_docker
    click.echo("You can optionally create an ML Flow MLproject file.")
    project_config["mlflow"] = PROJECT_CONFIG["mlflow"](project_config, True, default=False)
    project_config["git_init"] = git_init = PROJECT_CONFIG["git_init"](
        project_config,
        True,
        default=True,
    )
    if git_init:
        project_config["git_push"] = PROJECT_CONFIG["git_push"](
            project_config,
            True,
            default=False,
        )
        template["git_message"] = TEMPLATE["git_message"](
            template,
            True,
            default="Generate project files with mloq",
        )
    return project_config, template


def welcome_message():
    """Welcome message to be displayed during interactive setup."""
    click.echo(f"Welcome to the MLOQ {__version__} interactive setup utility.")
    click.echo()
    click.echo(
        "Please enter values for the following settings (just press Enter "
        "to accept a default value, if one is given in brackets).",
    )
    click.echo()


def setup_cmd(config_file, output, override: bool, interactive: bool) -> int:
    """Initialize a new project using ML Ops Quickstart."""
    config = read_config_safe(config_file)
    project_config, template = config["project_config"], config["template"]
    if interactive:
        welcome_message()
        data = generate_config_interactive(template=template, project_config=project_config)
        project_config, template = data
    else:
        project_config = generate_project_config(project_config=project_config)
        template = generate_template(template=template, project_config=project_config)
    config = {"project_config": project_config, "template": template}
    if interactive and click.confirm("Do you want to generate a mloq.yml file?"):
        write_config(config, output, safe=True)
    if not override and interactive:
        override = click.confirm("Do you want to override existing files?")
    try:
        setup_project(
            path=output,
            template=template,
            project_config=project_config,
            override=override,
        )
    except Failure as e:
        print(f"Failed to setup the project: {e}", file=sys.stderr)
        return 1
    return 0
