"""Mloq globals command implementation."""
import click
from omegaconf import DictConfig, OmegaConf
import param

from mloq.command import Command


class GlobalsCMD(Command):
    """Implement the functionality of the globals Command."""

    cmd_name = "globals"
    project_name = param.String(doc="Select project name")
    description = param.String(doc="Short description of the project")
    author = param.String(doc="Author(s) of the project")
    owner = param.String("${globals.author}", doc="Github handle of the project owner")
    email = param.String(doc="Owner contact email")
    open_source = param.Boolean(doc="Is the project Open Source?")
    project_url = param.String("???", doc="GitHub project url")
    default_branch = param.String("main", doc="Default branch of the project")
    license = param.String("MIT", doc="Project license type")
    use_poetry = param.Boolean(True, doc="Use poetry to manage dependencies?")
    main_python_version = param.String("3.8", doc="Python version for CI, Poetry and Docker")

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("The following values will occur in several places in the generated files.")
        return super(GlobalsCMD, self).interactive_config()

    def parse_config(self) -> DictConfig:
        """Generate the configuration of the project via a configuration file."""
        default_url = f"https://github.com/{self.owner}/{self.project_name.replace(' ', '-')}"
        self.project_url = OmegaConf.select(self.config, "project_url", default=default_url)
        self.conf.sync()
        return super(GlobalsCMD, self).parse_config()
