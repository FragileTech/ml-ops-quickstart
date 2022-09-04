"""Patch param to allow omegaconf Missing values and interpolation strings."""
from omegaconf import MISSING
import param as param_


__DEFAULT_MARK = "__DEFAULT_MARK__"


def __init__patched(self, default=__DEFAULT_MARK, **kwargs):
    """Handle missing values and interpolations trings when initializing a param.Parameter."""
    from mloq.config.configuration import is_interpolation

    is_missing = default == MISSING
    interpolated = is_interpolation(default)
    self._missing_init = is_missing
    self._interpolation_init = interpolated
    if is_missing or interpolated:
        kwargs["allow_None"] = True
        default = None
    elif default == __DEFAULT_MARK:
        param_class = getattr(param_, self.__class__.__name__)
        default = param_class().default
    super(self.__class__, self).__init__(default=default, **kwargs)


def _create_param__(item):
    """Patch the target param.Parameter to support missing values and interpolations strings."""
    base = getattr(param_, item)
    patched_class = type(
        item,
        (base,),
        {
            "__init__": __init__patched,
            "__slots__": list(base.__slots__) + ["_missing_init", "_interpolation_init"],
        },
    )
    return patched_class


PATCHED_PARAMETERS = {"String", "Integer", "Number", "Tuple", "Dict", "List", "ListSelector"}


class __ParamPatcher:
    """Patch the param package to handle missing values and interpolation strings."""

    PATCHED_PARAMETERS = PATCHED_PARAMETERS

    def __getattr__(self, item):
        """Patch the parameters included in PATCHED_PARAMETERS."""
        if item in PATCHED_PARAMETERS:
            return _create_param__(item)
        return getattr(param_, item)

    def __setattr__(self, key, value):
        """Read only monkeypatching."""
        raise NotImplementedError


param = __ParamPatcher()
