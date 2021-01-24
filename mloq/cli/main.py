"""Command line interface for mloq."""
import click

from mloq.api import setup_repository
from mloq.config.generation import generate_project_config, generate_template
from mloq.config.logic import read_config_safe, write_config


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

interactive_opt = click.option(
    "--interactive/--no-interactive",
    "-i/ ",
    default=False,
    show_default=True,
    help="If True the configuration values will be defined interactively on the command line.",
)


@click.group()
def cli():
    """Command line interface for ML Ops Quickstart."""
    pass


@cli.command()
@override_opt
@interactive_opt
@config_file_opt
@output_path_arg
def setup(config_file, output, override: bool, interactive: bool):
    """Initialize a new project using ML Ops Quickstart."""
    config = read_config_safe(config_file)
    project, template = config["project_config"], config["template"]
    if interactive:
        click.echo("Welcome to MLOQ, let's set up a new project!")
        click.echo("Please define the type of project that mloq will set up")
    project = generate_project_config(project_config=project, interactive=interactive)
    if interactive:
        click.echo("Please fill in the parameters needed to configure the project")
    template = generate_template(
        template=template, project_config=project, interactive=interactive
    )
    config = {"project_config": project, "template": template}
    if click.confirm("Do you want to generate a mloq.yml file?"):
        write_config(config, output, safe=True)
    if not override and interactive:
        override = click.confirm("Do you want to override existing files?")
    setup_repository(path=output, template=template, project_config=project, override=override)
