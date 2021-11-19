from omegaconf import MISSING
import param as param_
import pytest

from mloq.config.param_patch import param


patched_classes = [getattr(param, p) for p in sorted(param.PATCHED_PARAMETERS)]


@pytest.fixture(scope="module", params=patched_classes)
def patched_class(request):
    return request.param


class TestParamPatch:
    def test_init_default(self, patched_class):
        instance = patched_class()
        param_class = getattr(param_, patched_class.__name__)
        assert isinstance(instance, param_class)

    def test_init_missing(self, patched_class):

        instance = (
            patched_class(MISSING, length=3)
            if patched_class.__name__ == "Tuple"
            else patched_class(MISSING)
        )
        assert instance.default is None
        assert instance._missing_init

    def test_init_interpolation(self, patched_class):

        instance = (
            patched_class("${global}", length=3)
            if patched_class.__name__ == "Tuple"
            else patched_class("${global}")
        )
        assert instance.default is None
        assert instance._interpolation_init
