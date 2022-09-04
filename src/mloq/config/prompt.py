"""This file contains the logic defining all the parameters needed to \
set up a project with mloq."""
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import click
from omegaconf import DictConfig, MISSING, OmegaConf
import param

from mloq.config.configuration import as_resolved_dict, Configurable
from mloq.config.custom_click import confirm, prompt
from mloq.failure import MissingConfigValue


Choices = Union[List[str], Tuple[str], Set[str]]


class PromptParam:
    """
    Defines a configuration parameter.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yaml
        3. Interactive promp from CLI (Optional)
    """

    def __init__(self, name: str, target: Configurable, **kwargs):
        """
        Initialize a ConfigParam.

        Args:
            name: Name of the parameter (as defined in mloq.yaml).
            text: Text that will be prompted in the CLI when using interactive mode.
            **kwargs: Passed to click.prompt when running in interactive mode.
        """
        self.name = name
        self._target = target
        prompt_text = self.param.doc if self.param.doc else self.name
        self._prompt_text = click.style(f"> {prompt_text}", fg="bright_magenta", reset=False)
        self._prompt_kwargs = kwargs
        self._prompt_kwargs["show_default"] = kwargs.get("show_default", True)
        self._prompt_kwargs["type"] = kwargs.get("type", str)

    @property
    def param(self) -> param.Parameter:
        """Get the param.Parameter object corresponding to the current configuration parameter."""
        return getattr(self._target.param, self.name)

    @property
    def value(self) -> Any:
        """Return the value of the configuration parameter."""
        return getattr(self._target, self.name)

    @property
    def config(self) -> Any:
        """Return the value of the parameter as defined in its config DictConfig."""
        if self.name not in self._target.config:
            raise MissingConfigValue(f"Config value {self.name} is not defined in config")
        elif OmegaConf.is_missing(self._target.config, self.name):
            return MISSING
        return self._target.config[self.name]

    def __call__(
        self,
        interactive: bool = False,
        default: Optional[Any] = None,
        **kwargs,
    ):
        """
        Return the value of the parameter parsing it from the different input sources available.

        Args:
            interactive: Prompt the user to input the value from CLI if it's not defined
                        in config or as en environment variable.
            default: Default value displayed in the interactive mode.
            **kwargs: Passed to click.prompt in interactive mode. Overrides the
                      values defined in __init__

        Returns:
            Value of the parameter.
        """
        value = default if default is not None else self.value
        value = self._prompt(value, **kwargs)
        return value

    def _prompt(self, value, **kwargs):
        """Prompt user for value."""
        _kwargs = dict(self._prompt_kwargs)
        _kwargs.update(kwargs)
        if value is not None:
            _kwargs["default"] = value
        return prompt(self._prompt_text, **_kwargs)


class MultiChoicePrompt(PromptParam):
    """
    Define a configuration parameter that can take multiple values \
    from a pre-defined set of values.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yaml
        3. Interactive promp from CLI (Optional)
    """

    def __init__(
        self,
        name: str,
        target: Configurable,
        choices: Optional[Choices] = None,
        **kwargs,
    ):
        """
        Initialize a ConfigParam.

        Args:
            name: Name of the parameter (as defined in mloq.yaml).
            choices: Contains all the available values for the parameter.
            text: Text that will be prompted in the CLI when using interactive mode.
            **kwargs: Passed to click.prompt when running in interactive mode.
        """
        kwargs["type"] = str
        super(MultiChoicePrompt, self).__init__(name=name, target=target, **kwargs)
        self.choices = choices  # TODO: use this to validate user input.

    def _prompt(self, value, **kwargs) -> List[str]:
        """Transform the parsed string from the CLI into a list of selected values."""
        val = super(MultiChoicePrompt, self)._prompt(value, **kwargs)
        return self._parse_string(val) if isinstance(val, str) else val

    @staticmethod
    def _parse_string(value) -> List[str]:
        def filter_str(s):
            return s.lstrip().replace("'", "").replace('"', "").replace("[", "").replace("]", "")

        return [filter_str(s) for s in value.split(",")]


class StringPrompt(PromptParam):
    """
    Define a configuration parameter that can take a string value.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yaml
        3. Interactive promp from CLI (Optional)
    """

    def __init__(
        self,
        name: str,
        target: Configurable,
        **kwargs,
    ):
        """
        Initialize a ConfigParam.

        Args:
            name: Name of the parameter (as defined in mloq.yaml).
            choices: Contains all the available values for the parameter.
            text: Text that will be prompted in the CLI when using interactive mode.
            **kwargs: Passed to click.prompt when running in interactive mode.
        """
        kwargs["type"] = str
        super(StringPrompt, self).__init__(name=name, target=target, **kwargs)


class IntPrompt(PromptParam):
    """
    Define a configuration parameter that can take an integer value.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yaml
        3. Interactive promp from CLI (Optional)
    """

    def __init__(
        self,
        name: str,
        target: Configurable,
        **kwargs,
    ):
        """
        Initialize a ConfigParam.

        Args:
            name: Name of the parameter (as defined in mloq.yaml).
            choices: Contains all the available values for the parameter.
            text: Text that will be prompted in the CLI when using interactive mode.
            **kwargs: Passed to click.prompt when running in interactive mode.
        """
        kwargs["type"] = int
        super(IntPrompt, self).__init__(name=name, target=target, **kwargs)


class FloatPrompt(PromptParam):
    """
    Define a configuration parameter that can take a floating point value.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yaml
        3. Interactive promp from CLI (Optional)
    """

    def __init__(
        self,
        name: str,
        target: Configurable,
        **kwargs,
    ):
        """
        Initialize a ConfigParam.

        Args:
            name: Name of the parameter (as defined in mloq.yaml).
            choices: Contains all the available values for the parameter.
            text: Text that will be prompted in the CLI when using interactive mode.
            **kwargs: Passed to click.prompt when running in interactive mode.
        """
        kwargs["type"] = float
        super(FloatPrompt, self).__init__(name=name, target=target, **kwargs)


class BooleanPrompt(PromptParam):
    """
    Defines a boolean configuration parameter.

    It allows to parse a configuration value from different sources in the following order:
        1. Environment variable named as MLOQ_PARAM_NAME
        2. Values defined in mloq.yaml
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


PARAM_TO_PROMPT = {
    param.Boolean: BooleanPrompt,
    param.Integer: IntPrompt,
    param.Number: FloatPrompt,
    param.String: StringPrompt,
    param.ListSelector: MultiChoicePrompt,
    # TODO: MultiChoice, Choice
}


class Prompt:
    """
    Manage all the functionality needed to display a cli prompt.

    It allows to interactively define the values of the different parameters of a class.
    """

    def __init__(self, target: "Promptable"):
        """Initialize a Prompt."""
        self._target = target
        self._prompts = {}
        self._init_prompts()

    def __call__(self, key: str, inplace: bool = False, **kwargs) -> Any:
        """Display the a prompt to interactively define the parameter values of target."""
        return self.prompt(key=key, inplace=inplace, **kwargs)

    def _init_prompts(self) -> None:
        """Initialize the prompts corresponding to the target Promptable parameters."""
        self._prompts = {}
        conf: DictConfig = self._target.config
        param_ = self._target.param
        for name, value in as_resolved_dict(conf).items():
            param_inst = getattr(param_, name)
            type_ = type(param_inst)
            prompt_cls = PARAM_TO_PROMPT.get(type_)
            if prompt_cls is not None:
                default = value if value is not MISSING else param_inst.default
                self._prompts[name] = prompt_cls(name, self._target, default=default)

    def prompt(self, key: str, inplace: bool = False, **kwargs) -> Any:
        """Display the a prompt to interactively define the parameter values of target."""
        val = self._prompts[key](**kwargs)
        if inplace:
            setattr(self._target, key, val)
        else:
            return val

    def prompt_all(self, inplace: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Prompt all the target's parameters.

        Return a dictionary containing the provided values.
        """

        def param_precedence(x):
            val = getattr(self._target.param, x).precedence
            return (1e100 if val is None else val), x

        sorted_keys = sorted(self._prompts.keys(), key=param_precedence)
        return {k: self.prompt(key=k, inplace=inplace, **kwargs) for k in sorted_keys}


class Promptable(Configurable):
    """
    Configurable class that allows to define the parameter values interactively using CLI prompts.

    It contains a prompt attribute in charge of managing the prompting functionality for the
    param.Parameters defined.
    """

    def __init__(self, **kwargs):
        """Initialize a Promptable."""
        super(Promptable, self).__init__(**kwargs)
        self.prompt = Prompt(self)
