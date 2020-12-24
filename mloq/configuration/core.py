import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import click
from ruamel.yaml import load as yaml_load, Loader, YAML as RuamelYAML
from ruamel.yaml.compat import StringIO

from mloq.requirements import require_cuda


TEMPLATE_SCHEMA = {
    "project_name": None,
    "owner": None,
    "author": None,
    "email": None,
    "copyright_holder": None,
}
CONFIG_SCHEMA = {"template": {}}


def get_docker_python_version(params: dict) -> str:
    """Return the highest python version defined for the project."""
    max_version = list(sorted(params["template"]["python_versions"]))[-1]
    version = max_version.replace(".", "")
    return f"py{version}"


def set_docker_image(params) -> dict:
    """
    Add to params the base docker container that will be used to define the project's container.

    If the dependencies require cuda the base image will be gpu friendly.
    """
    if "base_docker_image" in params["template"]:
        return params
    v = get_docker_python_version(params)
    ubuntu_v = "ubuntu20.04" if v in ["py38", "py39"] else "ubuntu18.04"
    image = (
        f"fragiletech/{ubuntu_v}-cuda-11.0-{v}"
        if require_cuda(params)
        else f"fragiletech/{ubuntu_v}-base-{v}"
    )
    params["template"]["base_docker_image"] = image
    return params


def parse_python_versions(params: dict) -> dict:
    """Add Python 3.8 as a default supported version to the config dictionary."""
    if "python_versions" not in params["template"]:
        params["template"]["python_version"] = ["3.8"]
    # TODO (guillemdb): sanitize input and check for valid python version format
    return params


class StringYAML(RuamelYAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        RuamelYAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


class BaseEntry:
    def __init__(self, name: str, value=None, default=None):
        self._name = name
        self._value = value
        self._default = default

    def __repr__(self):
        return f"{self.__class__.__name__} {self.name} value: {self.value}"

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return (
            self.main_value()
            if self._value is not None
            else os.environ.get(self.env_var_name, self.default)
        )

    @property
    def default(self):
        if isinstance(self._default, BaseEntry):
            return self._default.value
        elif callable(self._default):
            return self._default()
        else:
            return self._default

    @property
    def env_var_name(self):
        return f"MLOQ_{self.name.upper()}"

    def update(self, value):
        self._value = value

    def is_defined(self):
        return self.value is not None

    def main_value(self):
        if isinstance(self._value, BaseEntry):
            return self._value.value
        elif callable(self._value):
            return self._value()
        else:
            return self._value


class ConfigEntry(BaseEntry):
    def __init__(
        self,
        name: str,
        *name_args,
        value=None,
        prompt_text: str = None,
        hide_input: bool = False,
        show_default: bool = True,
        show_choices: bool = True,
        type=None,
        help: str = None,
        hidden: bool = False,
        prompt_suffix: str = ": ",
        show_envvar: bool = False,
        default_prompt=None,
        force_prompt=False,
        **kwargs,
    ):
        super(ConfigEntry, self).__init__(name=name, value=value, default=default_prompt)
        self._prompt_text, self._help = self._share_text(prompt_text, help, name)
        self._hide_input = hide_input
        self.force_prompt = force_prompt
        self._prompt_suffix = prompt_suffix
        self._type = type
        self._show_default = show_default
        self._show_choices = show_choices
        self._option = self._init_option(
            name_args,
            hide_input=self._hide_input,
            show_default=show_default,
            show_choices=show_choices,
            type=self._type,
            help=self._help,
            hidden=hidden,
            show_envvar=show_envvar,
            **kwargs,
        )
        self._prompt = self._init_prompt(
            text=self._prompt_text,
            hide_input=self._hide_input,
            type=self._type,
            prompt_suffix=self._prompt_suffix,
            show_default=self._show_default,
            show_choices=self._show_choices,
        )

    @property
    def option(self):
        return self._option

    def prompt(self):
        return self._prompt()

    def define_value(self, value: None):
        if value is not None:
            self._default = value
            self._value = value
            self._prompt = self._init_prompt(
                text=self._prompt_text,
                hide_input=self._hide_input,
                type=self._type,
                prompt_suffix=self._prompt_suffix,
                show_default=self._show_default,
                show_choices=self._show_choices,
            )
        if value is None or self.force_prompt:
            value = self.prompt()
        self.update(value)

    def _share_text(self, prompt_text, help, name):
        if prompt_text is None:
            prompt_text = name if help is None else help
        if help is None:
            help = prompt_text
        return prompt_text, help

    def _init_option(
        self,
        name_args,
        type,
        help,
        show_default,
        hide_input,
        hidden,
        show_choices,
        show_envvar,
        **attrs,
    ):
        return click.option(
            f"--{self.name.replace('_', '-')}",
            *name_args,
            default=lambda: self.value,
            show_default=(f"${self.env_var_name}" if self.default is None else show_default),
            hide_input=hide_input,
            type=type,
            help=help,
            hidden=hidden,
            show_choices=show_choices,
            show_envvar=show_envvar,
            prompt=False,
            confirmation_prompt=False,
            is_flag=None,
            flag_value=None,
            multiple=False,
            count=False,
            allow_from_autoenv=True,
            **attrs,
        )

    def _init_prompt(self, **prompt_kwargs):
        return lambda: click.prompt(default=self.value, **prompt_kwargs)


class MultiChoiceConfig(ConfigEntry):
    def __init__(self, name, choices, **kwargs):
        super(MultiChoiceConfig, self).__init__(name=name, **kwargs)
        self._choices = choices

    @property
    def choices(self):
        return self._choices

    def update(self, value):
        self._value = self._parse_string(value)

    def define_value(self, value: None):
        if value is None or self.force_prompt:
            value = self.prompt()
        value = self._parse_string(value)
        self.update(value)

    def _parse_string(self, value):
        def filter_str(s):
            return s.lstrip().replace("'", "").replace('"', "").replace("[", "").replace("]", "")

        if isinstance(value, str):
            return [filter_str(s) for s in value.split(",")]
        return value


class ConfigGroup:
    def __init__(
        self,
        name,
        entries: Union[
            List[Union[ConfigEntry, "ConfigGroup"]], Tuple[Union[ConfigEntry, "ConfigGroup"]]
        ],
    ):
        self._entries = {e.name: e for e in entries}
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def entries(self):
        return self._entries

    @property
    def option(self):
        def inner(func):
            for entry in self.entries.values():
                func = entry.option(func)
            return func

        return inner

    @property
    def value(self):
        return self.to_dict()

    def has_entry(self, entry: Union[str, ConfigEntry, "ConfigGroup"]) -> bool:
        def simple_has_entry(e):
            return (entry if isinstance(entry, str) else entry.name) in self._entries

        if isinstance(entry, (ConfigEntry, str)):
            return simple_has_entry(entry)
        elif isinstance(entry, ConfigEntry):
            return any([simple_has_entry(e) for e in entry.entries.values()])

    def delete(self, entry: Union[ConfigEntry, str], key_error: bool = True):
        if not self.has_entry(entry):
            if key_error:
                raise ValueError(f"Only ConfigEntry objects allowed, got {type(entry)} instead.")
            return
        name = entry if isinstance(entry, str) else entry.name
        del self._entries[name]

    def __getitem__(self, item):
        return self._entries[item]

    def __setitem__(self, key, value):
        self._entries[key] = value

    def get(self, item, default=None):
        return self._entries.get(item, default=default)

    def update(self, entry: ConfigEntry):
        if not isinstance(entry, ConfigEntry):
            raise ValueError(f"Only ConfigEntry objects allowed, got {type(entry)} instead.")
        self._entries[entry.name] = entry

    def to_dict(self) -> Dict[str, Any]:
        return {e.name: e.value for e in self._entries.values()}

    def to_kwargs(self, default=None):
        """Return a shallow dictionary containing the names and values of all \
         ConfigEntry objects."""
        kwargs = {} if default is None else default
        for entry in self.entries.values():
            if isinstance(entry, ConfigEntry):
                kwargs[entry.name] = entry.value
            elif isinstance(entry, ConfigGroup):
                for child_ent in entry.entries.values():
                    if isinstance(child_ent, ConfigEntry):
                        kwargs[child_ent.name] = child_ent.value
                    elif isinstance(child_ent, ConfigGroup):
                        kwargs.update(child_ent.to_kwargs(kwargs))
        return kwargs

    def define_value(self, **kwargs):
        for name, entry in self._entries.items():
            entry.define_value(kwargs.get(name))


class Config:
    def __init__(
        self,
        entries: Union[
            List[Union[ConfigEntry, ConfigGroup]], Tuple[Union[ConfigEntry, ConfigGroup]]
        ],
    ):
        self._entries = {e.name: e for e in entries}

    def __getitem__(self, item):
        return self._entries[item]

    def __setitem__(self, key, value):
        self._entries[key] = value

    @property
    def entries(self):
        return self._entries

    @property
    def option(self):
        def inner(func):
            for entry in self.entries.values():
                func = entry.option(func)
            return func

        return inner

    def click_command(self, group):
        def wrapped(func):
            @group.command(name=func.__name__)
            @self.option
            def inner(**kwargs):
                self.define_value(**kwargs)
                func(**self.to_kwargs())

            inner.__name__ = func.__name__
            return inner

        return wrapped

    def to_dict(self) -> Dict[str, Any]:
        return {e.name: e.value for e in self._entries.values()}

    def to_kwargs(self, default=None):
        kwargs = {} if default is None else default
        for entry in self.entries.values():
            if isinstance(entry, ConfigEntry):
                kwargs[entry.name] = entry.value
            elif isinstance(entry, ConfigGroup):
                for child_ent in entry.entries.values():
                    if isinstance(child_ent, ConfigEntry):
                        kwargs[child_ent.name] = child_ent.value
                    elif isinstance(child_ent, ConfigGroup):
                        kwargs.update(child_ent.to_kwargs(kwargs))
        return kwargs

    def define_value(self, **kwargs):
        """Kwargs is a loaded configuration dict."""
        for name, entry in self._entries.items():
            print("defining", name, entry)
            if isinstance(entry, ConfigGroup):
                entry.define_value(**kwargs.get(entry.name))
            elif isinstance(entry, ConfigEntry):
                entry.define_value(kwargs.get(name))


class BaseWrapper:
    """Generic wrapper to wrap any of the other classes."""

    def __init__(self, data, name: str = "_unwrapped"):
        """
        Initialize a :class:`BaseWrapper`.

        Args:
            data: Object that will be wrapped.
            name: Assign a custom attribute name to the wrapped object.

        """
        setattr(self, name, data)
        self.__name = name

    @property
    def unwrapped(self):
        """Access the wrapped object."""
        return getattr(self, self.__name)

    def __repr__(self):
        return self.unwrapped.__repr__()

    def __call__(self, *args, **kwargs):
        """Call the wrapped class."""
        return self.unwrapped.__call__(*args, **kwargs)

    def __str__(self):
        return self.unwrapped.__str__()

    def __len__(self):
        return self.unwrapped.__len__()

    def __getattr__(self, attr):
        # If a BaseWrapper is being wrapped forward the attribute to it
        if isinstance(self.unwrapped, BaseWrapper):
            return getattr(self.unwrapped, attr)
        return self.unwrapped.__getattribute__(attr)


class ConfigFile(BaseWrapper):
    DEFAULT_FILE_NAME = "mloq.yml"

    def __init__(
        self,
        config: Config,
        file: Optional[Union[Path, str]] = None,
        target: Optional[Union[Path, str]] = None,
    ):
        super(ConfigFile, self).__init__(config, name="config")
        self._source = file if file is None else Path(file)
        self._source_is_file = self.validate_path(self.source) and self.source.is_file()
        self._file_name = self.source.name if self._source_is_file else self.DEFAULT_FILE_NAME
        # Load target path data
        self._target = target if target is None else Path(target)
        self._target_is_file = self.validate_path(self.target) and self.target.is_file()
        self._target_name = self.target.name if self._target_is_file else self.DEFAULT_FILE_NAME
        source_is_valid = self.validate_path(self.source)
        self._data = self.read_config(self.source, fail_ok=True) if source_is_valid else None

    def __repr__(self):
        return self.yaml_as_string(self.config.to_dict())

    @staticmethod
    def yaml_as_string(params):
        yaml = StringYAML()
        yaml.indent(sequence=4, offset=2)
        return yaml.dump(params)

    @classmethod
    def read_config(cls, path: Union[Path, str], fail_ok: bool = False) -> dict:
        """Load the project configuration from the target path."""
        if isinstance(path, Path):
            path = path / cls.DEFAULT_FILE_NAME if path.is_dir() else path
        try:
            with open(path, "r") as config:
                params = yaml_load(config.read(), Loader)
        except Exception as e:
            if fail_ok:
                return dict()
            raise e
        return params

    @property
    def source(self):
        if self._source is None:
            return
        elif isinstance(self._source, Path):
            return (
                self._source if self._source.is_file() else self._source / self.DEFAULT_FILE_NAME
            )
        raise ValueError(f"source is not a Path: {self._source}")

    @property
    def target(self):
        if self._target is None:
            return
        elif isinstance(self._target, Path):
            if self._target.is_file():
                return self._target
            elif self._target.is_dir() and self.source.is_file():
                return self._target / self.source.name
            else:
                return self._target / self.DEFAULT_FILE_NAME

        raise ValueError(f"source is not a Path: {self._target}")

    @property
    def data(self):
        return self._data

    @property
    def file_name(self):
        return self._file_name

    def set_file(self, file: Union[str, Path]):
        self._source = Path(file)

    def set_target(self, target: Union[Path, str]):
        self._target = Path(target)

    def validate_path(self, path: Path):
        path = Path(path) if isinstance(path, str) else path
        if isinstance(path, Path):
            return path.is_file() or (path / self.DEFAULT_FILE_NAME).is_file()
        return False

    @property
    def file_option(self):
        config_file_opt = click.option(
            "--file",
            "-f",
            "file",
            default=None,
            show_default=True,
            help="Name of the target config file. Defaults to mloq.yml if filename is a path.",
            type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
        )
        return config_file_opt

    @staticmethod
    def _update_kwargs_from_config(base, new):
        # FIXME: (guillemdb) handle defaults from file when default prompt is specified.
        def recursive_update(orig, updt):
            for k, v in dict(orig).items():
                if k in updt and updt[k] is None:
                    updt[k] = orig[k]
                elif isinstance(v, dict):
                    return recursive_update(v, updt)
            return updt

        return recursive_update(base, new)

    @staticmethod
    def _update_config_from_kwargs(conf, kwargs):
        def recursive_update(src, updt):
            for k, v in dict(src).items():
                if k in updt and updt[k] is not None:
                    src[k] = updt[k]
                elif isinstance(v, dict):
                    src[k] = recursive_update(src[k], updt)
                    return src
            return src

        return recursive_update(conf, kwargs)

    @staticmethod
    def write_yaml(data: dict, path: Union[Path, str]):
        yaml = RuamelYAML()
        yaml.indent(sequence=4, offset=2)
        with open(path, "w") as f:
            yaml.dump(data, f)

    def save_config(self, conf: dict, from_kwargs: bool = False):
        from mloq.configuration.config_values import DEFAULT_CONFIG

        conf = self._update_config_from_kwargs(DEFAULT_CONFIG, conf) if from_kwargs else conf
        output = self.source if self.target is None else self.target
        self.write_yaml(data=conf, path=output)

    def to_config(self, **kwargs):
        from mloq.configuration.config_values import DEFAULT_CONFIG

        return self._update_config_from_kwargs(DEFAULT_CONFIG, kwargs)

    def parse_config(self, config):
        config = parse_python_versions(config)
        return set_docker_image(config)

    @staticmethod
    def flatten_dict(d):
        new_d = {}
        for k, v in d.items():
            if isinstance(v, dict):
                new_d.update(v)
            else:
                new_d[k] = v
        return new_d

    def click_command(self, group, *options):
        def wrapped(func):
            @group.command(name=func.__name__)
            @self.file_option
            @self.option
            def inner(file, *args, **kwargs):
                print("INIT")
                our_kwargs_keys = self.to_kwargs()
                our_kwargs = {k: v for k, v in kwargs.items() if k in our_kwargs_keys}
                other_kwargs = {k: v for k, v in kwargs.items() if k not in our_kwargs_keys}
                if self.validate_path(file):
                    self.set_file(file)
                config = self.read_config(self.source, fail_ok=False)
                config = self._update_config_from_kwargs(config, our_kwargs)
                print("CONFIG", config)
                self.define_value(**config)
                func(*args, **{**other_kwargs, **self.to_kwargs()})

            for opt in options:
                inner = opt(inner)
            return inner

        return wrapped
