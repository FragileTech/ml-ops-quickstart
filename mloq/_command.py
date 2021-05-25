from pathlib import Path
import sys
from typing import Union
from unittest.mock import patch

import click
import hydra
from omegaconf import DictConfig

from mloq.api import setup_project
from mloq.cli.setup_cmd import generate_config_interactive, welcome_message
from mloq.config.logic import get_docker_image, write_config_setup
from mloq.config.params import is_empty, PROJECT, TEMPLATE
from mloq.config.setup_generation import _generate_project_config, _generate_template_config
from mloq.failure import Failure
from mloq.files import Ledger, setup_yml
from mloq.templating import write_template as wt


def load_config(config_file, hydra_args):  # load_config??
    config_file = Path(config_file if config_file else "mloq.yml")  # FIXME
    hydra_args = ["--config-dir", str(config_file.parent)] + list(hydra_args)
    config = DictConfig({})

    @hydra.main(config_name=config_file.name)
    def load_config(loaded_config: DictConfig):
        nonlocal config
        config = loaded_config

    with patch("sys.argv", [sys.argv[0]] + list(hydra_args)):
        load_config()

    return config


class SetupCommand:
    def __init__(
        self,
        config: DictConfig,
        output_directory: Union[Path, str],
        overwrite: bool,
        interactive: bool,
        only_config: bool,
        ledger: Ledger,
    ):

        self._config = config
        self._output_directory = Path(output_directory)
        self._overwrite = overwrite
        self._interactive = interactive
        self._only_config = only_config
        self.ledger = ledger
        self.file = setup_yml

    @property
    def config(self) -> DictConfig:
        return self._config

    @property
    def output_directory(self) -> Path:
        return self._output_directory

    @property
    def overwrite(self) -> bool:
        return self._overwrite

    @property
    def interactive(self) -> bool:
        return self._interactive

    @property
    def only_config(self) -> bool:
        return self._only_config

    def __call__(self, ledger=None):
        self.ledger = Ledger() if ledger is None else self.ledger
        if not isinstance(self.ledger, Ledger):
            raise ValueError("Please specify a Ledger")
        return self.run()

    def create_directories(self) -> None:
        raise NotImplementedError

    def write_templates(self) -> None:
        wt(
            file=self.file,
            config=self.config,
            path=self.output_directory,
            ledger=self.ledger,
            overwrite=self.overwrite,
        )

    def generate_config(self) -> DictConfig:
        # return generate_config(self.config)
        return DictConfig(
            {
                "project": _generate_project_config(config=self.config),
                "template": _generate_template_config(config=self.config),
            },
        )

    def interactive_config(self) -> DictConfig:
        # return generate_config_interactive(self.config)

        # General project information
        click.echo("The following values will occur in several places in the generated files.")
        project, template = self.config.project, self.config.template
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
            "Open Source projects will include the corresponding "
            "LICENSE file and a DCO.md file",
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
        click.echo(
            "    data-science: Common data science libraries such as numpy, pandas, sklearn..."
        )
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
            click.echo(
                "A bot account will be used to automatically bump the version of your project."
            )
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
            base_docker = get_docker_image(self.config)
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
        return self.config

    def run(self) -> int:
        if self.interactive:
            welcome_message()
            self._config = self.interactive_config()
        else:
            self._config = self.generate_config()
        if self.interactive and (
            self.only_config or click.confirm("Do you want to generate a mloq.yml file?")
        ):
            write_config_setup(self.config, self._output_directory, safe=True)
        if self.only_config:
            return 0
        if not self.overwrite and self.interactive:
            self._overwrite = click.confirm("Do you want to overwrite existing files?")
        try:
            setup_project(
                path=self._output_directory,
                config=self.config,
                overwrite=self.overwrite,
            )
        except Failure as e:
            print(f"Failed to setup the project: {e}", file=sys.stderr)
            return 1
        return 0
