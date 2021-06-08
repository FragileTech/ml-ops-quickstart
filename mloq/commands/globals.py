import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.params import BooleanParam, config_group, ConfigParam


_GLOBALS = [
    ConfigParam("project_name", "Select project name"),
    ConfigParam("description", "Short description of the project"),
    ConfigParam("author", "Author(s) of the project"),
    ConfigParam("owner", "Github handle of the project owner"),
    ConfigParam("email", "Owner contact email"),
    BooleanParam("open_source", "Is the project Open Source?"),
    ConfigParam("project_url", "GitHub project url"),
    ConfigParam("default_branch", "Default branch of the project"),
]


class GlobalsCMD(Command):
    name = "globals"
    CONFIG = config_group("GLOBALS", _GLOBALS)

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("The following values will occur in several places in the generated files.")
        return self.parse_config()

    def parse_config(self) -> DictConfig:
        """Generate the configuration of the project via a configuration file."""
        config = self.record.config.globals
        for param_name in self.CONFIG._fields:
            if param_name == "project_url":
                continue
            value = getattr(self.CONFIG, param_name)(config, self.interactive)
            setattr(config, param_name, value)
        default_url = f"https://github.com/{config.owner}/{config.project_name.replace(' ', '-')}"
        config.project_url = self.CONFIG.project_url(config, self.interactive, default=default_url)
        return self.record.config


def cli(*args, **kwargs):
    pass
