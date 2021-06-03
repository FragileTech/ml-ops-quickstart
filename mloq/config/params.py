"""This file contains the logic defining all the parameters needed to se up a project with mloq."""
import os
from typing import Any, List, NamedTuple, Optional, Set, Tuple, Union

import click
from omegaconf import DictConfig
import omegaconf.errors

from mloq.cli.custom_prompt import confirm, prompt


Choices = Union[List[str], Tuple[str], Set[str]]


class ConfigParam:
    """
    Defines a configuration parameter.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yml
        3. Interactive promp from CLI (Optional)
    """

    def __init__(self, name: str, text: Optional[str] = None, **kwargs):
        """
        Initialize a ConfigParam.

        Args:
            name: Name of the parameter (as defined in mloq.yml).
            text: Text that will be prompted in the CLI when using interactive mode.
            **kwargs: Passed to click.prompt when running in interactive mode.
        """
        self.name = name
        prompt_text = text if text is not None else self.name
        self._prompt_text = click.style(f"> {prompt_text}", fg="bright_magenta", reset=False)
        self._prompt_kwargs = kwargs
        self._prompt_kwargs["show_default"] = kwargs.get("show_default", True)
        self._prompt_kwargs["type"] = kwargs.get("type", str)

    def __call__(
        self,
        config: Optional[DictConfig] = None,
        interactive: bool = False,
        default: Optional[Any] = None,
        raise_error: bool = True,
        **kwargs,
    ):
        """
        Return the value of the parameter parsing it from the different input sources available.

        Args:
            config: Dictionary containing the configuration values defined in mloq.yml.
            interactive: Prompt the user to input the value from CLI if it's not defined \
                        in config or as en environment variable.
            default: Default value displayed in the interactive mode.
            raise_error: If True, a ValueError will be raise if the value is not defined. \
                         If False, return None when the value is not defined.
            **kwargs: Passed to click.prompt in interactive mode. Overrides the \
                      values defined in __init__

        Returns:
            Value of the parameter.
        """
        config = config or {}
        value = self._value_from_env()
        value = value if value is not None else self._value_from_config(config)
        value = value if value is not None else default
        if interactive:
            value = self._prompt(value, **kwargs)
        if value is None and raise_error:
            raise ValueError(f"Config value {self.name} is not defined.")
        return value

    def _value_from_env(self):
        """Return the config value if it is defined as an environment variable."""
        env_name = f"MLOQ_{self.name.upper()}"
        return os.environ.get(env_name)

    def _prompt(self, value, **kwargs):
        """Prompt user for value."""
        _kwargs = dict(self._prompt_kwargs)
        _kwargs.update(kwargs)
        if value is not None:
            _kwargs["default"] = value
        return prompt(self._prompt_text, **_kwargs)

    def _value_from_config(self, config: DictConfig):
        """Return the config value if it is present on the config dict."""

        def find_value(conf):
            for k in conf.keys():
                if k == self.name and omegaconf.OmegaConf.is_missing(conf, k):
                    return None
                elif k == self.name:
                    return conf[k]
                elif isinstance(conf[k], dict):
                    return find_value(conf[k])

        return find_value(config)


class MultiChoiceParam(ConfigParam):
    """
    Define a configuration parameter that can take multiple values \
    from a pre-defined set of values.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yml
        3. Interactive promp from CLI (Optional)
    """

    def __init__(
        self,
        name: str,
        choices: Optional[Choices] = None,
        text: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize a ConfigParam.

        Args:
            name: Name of the parameter (as defined in mloq.yml).
            choices: Contains all the available values for the parameter.
            text: Text that will be prompted in the CLI when using interactive mode.
            **kwargs: Passed to click.prompt when running in interactive mode.
        """
        kwargs["type"] = str
        super(MultiChoiceParam, self).__init__(name=name, text=text, **kwargs)
        self.choices = choices  # TODO: use this to validate user input.

    def _prompt(self, value, **kwargs) -> List[str]:
        """Transform the parsed string from the CLI into a list of selected values."""
        val = super(MultiChoiceParam, self)._prompt(value, **kwargs)
        return self._parse_string(val) if isinstance(val, str) else val

    def _value_from_env(self):
        """Return the config value if it is defined as an environment variable."""
        val = super(MultiChoiceParam, self)._value_from_env()
        return self._parse_string(val) if isinstance(val, str) else val

    @staticmethod
    def _parse_string(value) -> List[str]:
        def filter_str(s):
            return s.lstrip().replace("'", "").replace('"', "").replace("[", "").replace("]", "")

        return [filter_str(s) for s in value.split(",")]


class BooleanParam(ConfigParam):
    """
    Defines a boolean configuration parameter.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yml
        3. Interactive promp from CLI (Optional)
    """

    def _prompt(self, value, **kwargs):
        """Prompt user for value."""
        _kwargs = dict(self._prompt_kwargs)
        _kwargs.update(kwargs)
        if "type" in _kwargs:
            del _kwargs["type"]
        if value is not None:
            _kwargs["default"] = value
        return confirm(self._prompt_text, **_kwargs)


EMPTY_VALUES = {"none", "empty", "skip"}


def is_empty(value: Union[str, list, tuple, set]) -> bool:
    """
    Return True if a the target value is defined as an empty value.

    Empty values are defined in the configuration (are not None) but they are not \
    used by mloq. For example, empty values can be used to define empty project \
    requirements or no base Docker image.
    """
    if value is None or value == "???":
        return True
    elif isinstance(value, str):
        return value.lower() in EMPTY_VALUES
    elif not len(value):
        return True
    return any([v.lower() in EMPTY_VALUES for v in value])


def config_group(name, values):
    return NamedTuple(name, [(param.name, type(param)) for param in values])(*values)


_GLOBALS = [
    ConfigParam("project_name", "Select project name"),
    ConfigParam("owner", "Github handle of the project owner"),
    ConfigParam("email", "Owner contact email"),
    ConfigParam("author", "Author(s) of the project"),
    BooleanParam("open_source", "Is the project Open Source?"),
    ConfigParam("default_branch", "Default branch of the project"),
    ConfigParam("description", "Short description of the project"),
    ConfigParam("project_url", "GitHub project url"),
]

GLOBALS = config_group("GLOBALS", _GLOBALS)

_LICENSE = [
    BooleanParam("disable", "Disable license command?"),
    BooleanParam("open_source", "Is the project Open Source?"),
    ConfigParam(
        "license",
        "Project license type",
        type=click.Choice(["MIT", "Apache-2.0", "GPL-3.0", "None"], case_sensitive=False),
    ),
    ConfigParam("copyright_year", "Year when the project started"),
    ConfigParam("copyright_holder", "Copyright holder"),
]
_PROJECT = [
    BooleanParam("disable", "Disable project command?"),
    BooleanParam("docker", "Does the project contains a docker container?"),
    ConfigParam("owner", "Github handle of the project owner"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("description", "Short description of the project"),
    ConfigParam(
        "license",
        "Project license type",
        type=click.Choice(["MIT", "Apache-2.0", "GPL-3.0", "None"], case_sensitive=False),
    ),
]
PROJECT = config_group("PROJECT", _PROJECT)
_GIT = [
    BooleanParam("disable", "Disable git command?"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("git_message", "Initial Git commit message?"),
    BooleanParam("git_init", "Initialize Git repository?"),
    BooleanParam("git_push", "Execute git push to the target repository?"),
    ConfigParam("default_branch", "Default branch of the project"),
    ConfigParam("project_url", "GitHub project url"),
]
_DOCS = [
    BooleanParam("disable", "Disable docs command?"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("description", "Short description of the project"),
    ConfigParam("author", "Author(s) of the project"),
    ConfigParam("copyright_year", "Year when the project started"),
    ConfigParam("copyright_holder", "Copyright holder"),
]
DOCS = config_group("DOCS", _DOCS)
_PACKAGE = [
    BooleanParam("disable", "Disable package command?"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("pyproject_extra", "Additional pyproject.toml configuration"),
    MultiChoiceParam(
        "python_versions",
        text="Supported python versions",
        choices=["3.6", "3.7", "3.8", "3.9"],
    ),
    MultiChoiceParam(
        "requirements",
        text="Project requirements",
        choices=["data-science", "data-viz", "torch", "tensorflow", "none"],
    ),
]

_LINT = [
    BooleanParam("docstring_checks", "Enable/disable linting docstrings"),
    ConfigParam("pyproject_extra", "Additional pyproject.toml configuration"),
]

_DOCKER = [
    BooleanParam("disable", "Disable docker command?"),
    ConfigParam("docker_image", "Base docker image for the project's Docker container"),
    ConfigParam("docker_org", "Name of your docker organization"),
]
_CI = [
    BooleanParam("disable", "Disable ci command?"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("default_branch", "Default branch of the project"),
    ConfigParam("docker_org", "Name of your docker organization"),
    ConfigParam("bot_name", "Bot's GitHub login to push commits in CI"),
    ConfigParam("bot_email", "Bot account email"),
    ConfigParam("ci_python_version", "Primary Python version in GitHub Actions"),
    ConfigParam("ci_ubuntu_version", "Primary Ubuntu version in GitHub Actions"),
    ConfigParam("ci_extra", "Additional script in GitHub Actions before runnign the main tests"),
]
