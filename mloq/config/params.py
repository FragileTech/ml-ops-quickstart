import os
from typing import Any, Dict, List, Optional, Union

import click


Config = Dict[str, Union[None, str, Dict[str, Any], List[str]]]


class ConfigParam:
    def __init__(self, name, text: str, **kwargs):
        self.name = name
        self._prompt_text = text
        self._prompt_kwargs = kwargs
        self._prompt_kwargs["show_default"] = kwargs.get("show_default", True)
        self._prompt_kwargs["type"] = kwargs.get("type", str)

    def __call__(self, config: Config, interactive: bool, default: Optional[Any] = None, **kwargs):
        """Return the value of the parameter."""
        value = self._value_from_env()
        value = value if value is not None else self._value_from_config(config)
        value = value if value is not None else default
        if interactive:
            value = self._prompt(value, **kwargs)
        if value is None:
            raise ValueError(f"Config value {self.name} is not defined.")
        return value

    def _value_from_env(self):
        """Return the config value if it is defined as an environment variable"""
        env_name = f"MLOQ_{self.name.upper()}"
        return os.environ.get(env_name)

    def _prompt(self, value, **kwargs):
        """Prompt user for value."""
        _kwargs = dict(self._prompt_kwargs)
        _kwargs.update(kwargs)
        if value is not None:
            _kwargs["default"] = value
        return click.prompt(self._prompt_text, **_kwargs)

    def _value_from_config(self, config: Config):
        """Return the config value if it is present on the config dict."""

        def find_value(conf):
            for k, v in conf.items():
                if k == self.name:
                    return v
                elif isinstance(v, dict):
                    return find_value(v)

        return find_value(config)


class MultiChoiceParam(ConfigParam):
    def __init__(self, name, text: str, choices, **kwargs):
        kwargs["type"] = str
        super(MultiChoiceParam, self).__init__(name=name, text=text, **kwargs)
        self.choices = choices  # TODO: use this to validate user input.

    def _prompt(self, value, **kwargs) -> list:
        val = super(MultiChoiceParam, self)._prompt(value, **kwargs)
        return self._parse_string(val)

    @staticmethod
    def _parse_string(value) -> List[str]:
        def filter_str(s):
            return s.lstrip().replace("'", "").replace('"', "").replace("[", "").replace("]", "")

        return [filter_str(s) for s in value.split(",")]


class BooleanParam(ConfigParam):
    def _prompt(self, value, **kwargs):
        """Prompt user for value."""
        _kwargs = dict(self._prompt_kwargs)
        _kwargs.update(kwargs)
        if "type" in _kwargs:
            del _kwargs["type"]
        if value is not None:
            _kwargs["default"] = value
        return click.confirm(self._prompt_text, **_kwargs)


# MLOQ template parameters
project_name = ConfigParam("project_name", "Select project name")
owner = ConfigParam("owner", "Github handle of the project owner")
email = ConfigParam("email", "Owner contact email")
author = ConfigParam("author", "Author of the project")
copyright_holder = ConfigParam("copyright_holder", "Copyright holder")
project_url = ConfigParam("project_url", "GitHub project url")
bot_name = ConfigParam("bot_name", "Bot's GitHub login to push commits in CI")
bot_email = ConfigParam("bot_email", "Bot account email")
default_branch = ConfigParam("default_branch", "Default branch of the project")
description = ConfigParam("description", "Short description of the project")
docker_image = ConfigParam("docker_image", "Base docker image for the project's Docker container")
license_type = ConfigParam(
    "license", "Project license type", type=click.Choice(["MIT"], case_sensitive=False),
)
ci = ConfigParam(
    "ci",
    "Push workflow for Github Actions CI",
    type=click.Choice(["python", "dist", "none"], case_sensitive=False),
)
python_versions = MultiChoiceParam(
    "python_versions", "Supported python versions", choices=["3.6", "3.7", "3.8", "3.9"],
)
# MLOQ project parameters
requirements = MultiChoiceParam(
    "requirements",
    "Project requirements",
    choices=["data-science", "data-viz", "torch", "tensorflow", "none"],
)
proprietary = BooleanParam("proprietary", "Is the project proprietary?")
open_source = BooleanParam("open_source", "Is the project Open Source?")
use_docker = BooleanParam("docker", "Do you want to set up a Docker container?")
mlflow = BooleanParam("mlflow", "Do you want to set up ML Flow?")
# Dictionaries grouping the different sections of mloq.yml
PROJECT = {
    "requirements": requirements,
    "proprietary": proprietary,
    "open_source": open_source,
    "docker": use_docker,
    "ci": ci,
    "mlflow": mlflow,
}
TEMPLATE = {
    "project_name": project_name,
    "owner": owner,
    "email": email,
    "author": author,
    "copyright_holder": copyright_holder,
    "project_url": project_url,
    "bot_name": bot_name,
    "bot_email": bot_email,
    "default_branch": default_branch,
    "description": description,
    "license_type": license_type,
    "python_versions": python_versions,
    "docker_image": docker_image,
}
