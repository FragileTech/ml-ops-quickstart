import copy
import dataclasses
from dataclasses import field, make_dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import omegaconf
from omegaconf import Container, MISSING, OmegaConf
from omegaconf.errors import InterpolationToMissingValueError, MissingMandatoryValue
import param as param__
from typing_extensions import Protocol

from mloq.config.param_patch import param


#
try:
    from mypy.typeshed.stdlib.dataclasses import Field

    DClassField = Field[Any]
except ModuleNotFoundError:
    DClassField = Any


class Dataclass(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: Dict


ConfigValue = Any

ConfigurationDict = Union[Dict[Union[str, int, Enum, float, bool], ConfigValue]]

PythonType = Union[float, int, bool, str, list, dict, tuple]

ParamType = Union[
    param.Number,
    param.Integer,
    param.Boolean,
    param.String,
    param.Array,
    param.List,
    param.Dict,
    param.Tuple,
]

DataClassDict = Dict[str, Tuple[type, DClassField]]


class DictConfig(param.ClassSelector):
    def __init__(
        self,
        default: Optional[omegaconf.DictConfig] = None,
        doc: Optional[str] = None,
        instantiate: bool = True,
        per_instance: bool = True,
        **kwargs,
    ):
        default = omegaconf.DictConfig({}) if default is None else default
        if doc is None:
            doc = "Structured omegaconf.DictConfig representing the param.Parameters information"
        kwargs["class_"] = omegaconf.DictConfig

        super(DictConfig, self).__init__(
            default=default,
            doc=doc,
            instantiate=instantiate,
            per_instance=per_instance,
            **kwargs,
        )


PARAM_TO_TYPE = {
    param.Boolean: bool,
    param.Integer: int,
    param.Number: float,
    param.String: str,
    param.List: list,
    param.ListSelector: list,
    param.Dict: dict,
    param.Tuple: tuple,
    param__.Boolean: bool,
    param__.Integer: int,
    param__.Number: float,
    param__.String: str,
    param__.List: list,
    param__.ListSelector: list,
    param__.Dict: dict,
    param__.Tuple: tuple,
    DictConfig: omegaconf.DictConfig,
}


def param_to_dataclass_dict(
    obj: Union[param.Parameterized, Any],
) -> Dict[str, Tuple[type, DClassField]]:
    data = {}
    for k, v in obj.params().items():
        if k in ["name", "config"]:
            continue
        for param_type, _type in PARAM_TO_TYPE.items():
            if isinstance(v, param_type):
                value = getattr(obj, k) if isinstance(obj, param.Parameterized) else v.default
                data[k] = (_type, field(default=value))
                break
    return data


def param_to_dataclass(obj: Union[param.Parameterized, Any]) -> type:
    name = obj.__class__.name if isinstance(obj, param.Parameterized) else obj.name
    # FIXME: Assumes all keys are strings
    datac = make_dataclass(
        name,
        [(str(k), t, v) for k, (t, v) in param_to_dataclass_dict(obj).items()],
    )
    return datac


def param_to_omegaconf(obj: Union[param.Parameterized, Any]) -> omegaconf.DictConfig:
    return OmegaConf.structured(param_to_dataclass(obj))


def is_interpolation(s: str):
    if not isinstance(s, str):
        return False
    return "${" in s and "}" in s  # TODO: use regex


def to_param_type(obj, config, key):
    # Yaml cannot handle tuples, so we convert the value
    config = copy.deepcopy(config)
    OmegaConf.resolve(config)
    param_obj = obj.param.params().get(key)
    value = config[key] if not OmegaConf.is_missing(config, key) else param_obj.default
    if isinstance(value, omegaconf.ListConfig):
        value = [x for x in value]
    elif isinstance(value, omegaconf.DictConfig):
        value = {**value}
    type_ = PARAM_TO_TYPE.get(param_obj.__class__)
    if type_ and not isinstance(value, type_):
        if value is None:
            value = value if param_obj.allow_None else type_()
        else:
            value = type_(value)  # if value is not None else type_()

    return value


def to_config(
    config: Union[
        omegaconf.DictConfig,
        ConfigurationDict,
        Dataclass,
        param.Parameterized,
        None,
    ],
    **kwargs,
) -> omegaconf.DictConfig:
    if isinstance(config, param.Parameterized):
        config = param_to_omegaconf(config)
    elif dataclasses.is_dataclass(config):
        config = OmegaConf.structured(config, **kwargs)
    elif not isinstance(config, omegaconf.DictConfig):
        config = OmegaConf.create(config, **kwargs)
    elif config is None:
        return omegaconf.DictConfig({})
    return config


def resolve_as_dict(
    obj,
    config: Union[omegaconf.DictConfig, ConfigurationDict, Dataclass, param.Parameterized],
    **kwargs,
) -> ConfigurationDict:

    config: Union[Container, omegaconf.DictConfig] = to_config(config, **kwargs)
    OmegaConf.resolve(config)
    param_data: Dict[str, Any] = {k: to_param_type(obj, config, k) for k in config}
    return param_data


def safe_select(cfg, key, default=None):
    try:
        return OmegaConf.select(
            cfg=cfg,
            key=key,
            default=default,
            throw_on_resolution_failure=True,
            throw_on_missing=True,
        )
    except (MissingMandatoryValue, InterpolationToMissingValueError):  # , InterpolationKeyError):
        return MISSING


def as_resolved_dict(cfg):
    resolved_dict = {k: safe_select(cfg, k) for k in cfg.keys()}
    return resolved_dict


class OmegaConfInterface:
    def __init__(self, target, allow_missing: bool = False):
        self._target = target
        self.allow_missing = not allow_missing

    @property
    def config(self) -> omegaconf.DictConfig:
        return self._target.config

    @property
    def interpolations(self) -> ConfigurationDict:
        cont = OmegaConf.to_container(self.config, resolve=False)
        return {k: v for k, v in cont.items() if OmegaConf.is_interpolation(self.config, str(k))}

    @property
    def missing(self) -> List[Union[str, int, Enum, float, bool]]:
        return [k for k, v in as_resolved_dict(self.config).items() if v == MISSING]

    def _resolve_inplace(self, key: Optional[str] = None) -> None:
        if key is None:
            OmegaConf.resolve(self._target.config)
            return
        self.config[key] = self.select(key=key)

    def resolve(
        self,
        key: Optional[str] = None,
        inplace: bool = False,
    ) -> Union[Container, ConfigValue, None]:
        if inplace:
            return self._resolve_inplace(key)
        value = as_resolved_dict(self.config) if key is None else self.select(key=key)
        return value

    def is_missing(self, key: str) -> bool:
        return safe_select(self.config, key) == MISSING

    def is_interpolation(self, key: str) -> bool:
        return OmegaConf.is_interpolation(self.config, key)

    def select(self, key, default=None):
        return safe_select(self.config, key=key, default=default)


class BaseConfig(OmegaConfInterface):
    def __init__(
        self,
        target: "Configurable",
        config: Optional[Union[ConfigurationDict, omegaconf.DictConfig]] = None,
        cfg_node: Optional[str] = None,
        allow_missing: bool = False,
        **kwargs,
    ):
        super(BaseConfig, self).__init__(target=target, allow_missing=allow_missing)
        self._setup_config(config, cfg_node=cfg_node, **kwargs)

    def __getitem__(self, item: str) -> Any:
        return self.config[item]

    def __setitem__(self, key: str, value) -> Any:
        self.config[key] = value

    def to_container(self, resolve: bool = False, **kwargs):
        try:
            return OmegaConf.to_container(self.config, resolve=resolve, **kwargs)
        except (MissingMandatoryValue, InterpolationToMissingValueError):
            d = omegaconf.DictConfig(as_resolved_dict(self.config))
            return OmegaConf.to_container(d, resolve=resolve, **kwargs)

    @staticmethod
    def _resolve_node(
        kwargs: dict,
        config: Optional[omegaconf.DictConfig] = None,
        cfg_node: Optional[str] = None,
    ) -> omegaconf.DictConfig:
        kwsconf = OmegaConf.create(kwargs)
        if not config:
            return kwsconf
        # FIXME: IF we resolve at init to get the global conf value we loose the interpolations
        is_node = config and cfg_node is not None
        resolved_node = config  # omegaconf.DictConfig(as_resolved_dict(config))
        if is_node and cfg_node in config:
            resolved_node = config[cfg_node]
        resolved_with_kws = OmegaConf.merge(kwsconf, resolved_node)

        if is_node:
            # node_conf = OmegaConf.create({cfg_node: resolved_with_kws})
            # full_conf = OmegaConf.merge(config, node_conf)
            # OmegaConf.resolve(full_conf)
            # full_conf = OmegaConf.create(as_resolved_dict(full_conf))
            config[cfg_node] = resolved_with_kws
            return config[cfg_node]
        return resolved_with_kws

    def _setup_config(
        self,
        config: Optional[Union[ConfigurationDict, omegaconf.DictConfig]] = None,
        cfg_node: Optional[str] = None,
        **kwargs,
    ):
        conf = self._resolve_node(kwargs=kwargs, cfg_node=cfg_node, config=config)
        OmegaConf.set_struct(conf, True)
        self._target.config = conf  # TODO: make param.config constant


class Config(BaseConfig):
    @property
    def params(self) -> Dict[str, param.Parameter]:
        return self._target.param.params()

    def resolve(
        self,
        key: Optional[str] = None,
        inplace: bool = False,
    ) -> Union[Container, ConfigValue, None]:
        rsl = super(Config, self).resolve(inplace=inplace)
        if not inplace:
            value = rsl if key is None else self.to_param_type(key)
            return value

    def to_param_type(self, key):
        value = self.select(key)
        param_obj = self.params.get(key)
        if value == MISSING:
            return param_obj.default
        # Yaml cannot handle python data types such as tuples, so we cast value
        # to the appropriate type after reading data from the the DictConfig
        # and before setting the corresponding param.key
        if isinstance(value, omegaconf.ListConfig):
            value = [x for x in value]
        type_ = PARAM_TO_TYPE.get(param_obj.__class__)
        if isinstance(param_obj, param.Tuple):
            raise ValueError("TUPLE")
        if type_ and not isinstance(value, type_):
            if value is None:
                value = value if param_obj.allow_None else type_()
            else:
                value = type_(value)
        return value

    def dataclass_dict(
        self,
        ignore: Optional[Union[list, set, tuple, str]] = None,
    ) -> DataClassDict:
        data = {}
        ignored = {"name", "config"} if ignore is None else ignore
        ignored = set([ignored]) if isinstance(ignored, str) else ignored
        for k, v in self.params.items():
            if k in ignored:
                continue
            for param_type, _type in PARAM_TO_TYPE.items():
                if isinstance(v, param_type):
                    value = v.default if self._target is None else getattr(self._target, k)
                    data[k] = (_type, field(default=value))
                    break
        return data

    def to_dataclass(self) -> type:  # DataClass class, not an instance
        tgt = self._target
        name = tgt.__class__.__name__ if isinstance(tgt, Configurable) else tgt.__name__
        dclass = make_dataclass(name, [(k, t, v) for k, (t, v) in self.dataclass_dict().items()])
        return dclass

    def to_dictconfig(self) -> DictConfig:
        return OmegaConf.structured(self.to_dataclass())

    def sync(self):
        for k in self.config.keys():
            super(Configurable, self._target).__setattr__(k, self.to_param_type(k))

    def _setup_config(
        self,
        config: Optional[Union[ConfigurationDict, DictConfig]] = None,
        cfg_node: Optional[str] = None,
        **kwargs,
    ):
        ignored = {"name", "config"}
        # Make sure the DictConfig is initialized with all the params as keys
        kwargs = {k: kwargs.get(k, v.default) for k, v in self.params.items() if k not in ignored}
        super(Config, self)._setup_config(config=config, cfg_node=cfg_node, **kwargs)
        self.sync()


CONF_ATTRS = {"config", "conf", "_conf"}


class Configurable(param.Parameterized):

    config = DictConfig(readonly=False, per_instance=True, instantiate=True)

    def __init__(
        self,
        config: Optional[Union[ConfigurationDict, DictConfig]] = None,
        throw_on_missing: bool = True,
        cfg_node: Optional[str] = None,
        **kwargs,
    ):
        interp_kwargs = resolve_as_dict(self, kwargs)
        super(Configurable, self).__init__(**interp_kwargs)
        self.__conf = Config(
            self,
            config,
            cfg_node=cfg_node,
            throw_on_missing=throw_on_missing,
            **kwargs,
        )

    @property
    def conf(self) -> Config:
        return self.__conf

    def __setattr__(self, key, value):
        is_interp = is_interpolation(value)
        if value == MISSING or is_interp:
            self.config[key] = value
            value = (
                self.conf.to_param_type(key=key) if is_interp else self.param.params()[key].default
            )
        # Update the config dict as well as the parameters. Ignored during __init__ of parent class
        elif key in self.param.params() and hasattr(self, "conf"):
            self.config[key] = value
            value = self.conf.to_param_type(key=key)

        super(Configurable, self).__setattr__(key, value)

    def __getattr__(self, item):
        if item != "config" and OmegaConf.is_missing(self.config, item):
            return MISSING
        return super(Configurable, self).__getattr__(item)
