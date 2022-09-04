import omegaconf
import param
import pytest

from mloq.config.configuration import Configurable


class ConfigurableTest(Configurable):
    number = param.Number()
    integer = param.Integer()
    boolean = param.Boolean()
    string = param.String()
    list_ = param.List()
    dict_ = param.Dict()
    tuple_ = param.Tuple(default=(0, "miau", 3))


defaults = {
    "number": 16.02,
    "integer": 160290,
    "boolean": True,
    "list_": [0, 1, 2],
    "dict_": {"hola": "adios", "eleven": 11},
    "tuple_": (0, "miau", 3),
}

defaults_with_config = {
    "number": 16.02,
    "integer": 160290,
    "boolean": True,
    "list_": [0, 1, 2],
    "dict_": {"hola": "adios", "eleven": 11},
    "tuple_": (0, "miau", 3),
    "config": omegaconf.DictConfig(
        {
            "number": 16.02,
            "integer": 160290,
            "boolean": True,
            "list_": [0, 1, 2],
            "dict_": {"hola": "adios", "eleven": 11},
            "tuple_": (0, "miau", 3),
        },
    ),
}

only_config = {
    "config": omegaconf.DictConfig(
        {
            "number": 16.02,
            "integer": 160290,
            "boolean": True,
            "list_": [0, 1, 2],
            "dict_": {"hola": "adios", "eleven": 11},
            "tuple_": (0, "miau", 3),
        },
    ),
}

interp_no_conf = {
    "number": 160290.0,
    "integer": "${number}",
    "boolean": True,
    "list_": [0, 1, 2],
    "dict_": {},
    "tuple_": (0, "miau", 3),
}

interp_only_conf = {
    "config": omegaconf.DictConfig(
        {
            "number": 160290.0,
            "integer": "${number}",
            "boolean": True,
            "list_": [0, 1, 2],
            "dict_": {"hola": "adios", "eleven": 11},
            "tuple_": (0, "miau", 3),
        },
    ),
}

interpolated_both = {
    "number": 16.0,
    "integer": "${number}",
    "boolean": True,
    "list_": [0, 1, 2],
    "dict_": None,
    "tuple_": (0, "miau", 3),
    "config": omegaconf.DictConfig(
        {
            "number": 160290.0,
            "integer": "${number}",
            "boolean": True,
            "list_": [0, 1, 2],
            "dict_": {"hola": "adios", "eleven": 11},
            "tuple_": (0, "miau", 3),
        },
    ),
}

missing_no_conf = {
    "number": "???",
    "integer": "${number}",
    "boolean": True,
    "list_": [0, 1, 2],
    "dict_": {"hola": "adios", "eleven": 11},
    "tuple_": (0, "miau", 3),
}

missing_only_conf = {
    "config": omegaconf.DictConfig(
        {
            "number": 160290.0,
            "integer": "${number}",
            "boolean": "???",
            "list_": [0, 1, 2],
            "dict_": {"hola": "adios", "eleven": 11},
            "tuple_": (0, "miau", 3),
        },
    ),
}

missing_both_different = {
    "number": "???",
    "integer": "${number}",
    "boolean": True,
    "list_": [0, 1, 2],
    "dict_": {"hola": "adios", "eleven": 11},
    "tuple_": (0, "miau", 3),
    "config": omegaconf.DictConfig(
        {
            "number": 160290.0,
            "integer": "${number}",
            "boolean": True,
            "list_": [0, 1, 2],
            "dict_": {"hola": "adios", "eleven": 11},
            "tuple_": "???",
        },
    ),
}
missing_both_same = {
    "number": 16.0,
    "integer": "${number}",
    "boolean": "???",
    "list_": [0, 1, 2],
    "dict_": {"hola": "adios", "eleven": 11},
    "tuple_": (0, "miau", 3),
    "config": omegaconf.DictConfig(
        {
            "number": 160290.0,
            "integer": "${number}",
            "boolean": "???",
            "list_": [0, 1, 2],
            "dict_": {"hola": "adios", "eleven": 11},
            "tuple_": (0, "miau", 3),
        },
    ),
}

basic_params = [{}, defaults, defaults_with_config]

missing_params = [missing_no_conf, missing_only_conf, missing_both_same, missing_both_different]

interpolated_params = [interp_no_conf, interp_only_conf, interpolated_both]

configurable_params = basic_params + interpolated_params + missing_params


@pytest.fixture(scope="function", params=tuple(configurable_params))
def configurable(request):
    return ConfigurableTest(**request.param)


@pytest.fixture(scope="function", params=tuple(interpolated_params))
def interpolated(request):
    return ConfigurableTest(**request.param)


@pytest.fixture(scope="function", params=tuple(missing_params))
def missing(request):
    return ConfigurableTest(**request.param)
