from itertools import product

import omegaconf
from omegaconf import MISSING, OmegaConf
import param
import pytest

from mloq.config.configuration import Config, DictConfig, is_interpolation
from tests.config.fixtures import (
    configurable,
    ConfigurableTest,
    interpolated,
    interpolated_params,
)


def interpolation_is_consistent(
    configurable_,
    key,
):
    c = configurable_.conf
    itps = c.interpolations
    unresolved = OmegaConf.to_container(configurable_.config, resolve=False)
    assert key in unresolved
    assert len(itps) > 0
    assert key in itps
    assert c.is_interpolation(key)
    raw_value = unresolved[key]
    param_value = getattr(configurable_, key)
    assert isinstance(raw_value, str)
    assert raw_value != param_value
    if not isinstance(getattr(configurable_.param, key), param.String):
        assert not isinstance(param_value, str)
    return True


def missing_is_consistent(configurable, key, is_missing: False) -> bool:
    c = configurable.config
    is_miss = OmegaConf.is_missing(c, key)
    assert is_miss and is_missing
    if not is_miss:
        return True

    with pytest.raises(omegaconf.errors.MissingMandatoryValue):
        OmegaConf.to_container(c, throw_on_missing=True)


class TestConfig:
    def test_init(self, configurable):
        pass

    def test_attributes(self, configurable):
        c = configurable.conf
        assert isinstance(c.config, omegaconf.DictConfig)
        interp = c.interpolations
        assert isinstance(interp, dict)
        for k, v in interp.items():
            assert isinstance(k, str)
            assert isinstance(v, str)
            assert is_interpolation(v)

        for x in c.missing:
            assert isinstance(x, str)
            assert x in configurable.config.keys()
            if not omegaconf.OmegaConf.is_interpolation(configurable.config, x):
                assert omegaconf.OmegaConf.is_missing(configurable.config, x)

    @pytest.mark.parametrize("key, inplace", product([None, "integer", "number"], [True, False]))
    def test_resolve_does_not_crash(self, configurable, inplace, key):
        configurable.conf.resolve(key=key, inplace=inplace)

    def test_resolve_inplace_not_key(self, configurable):
        interps = configurable.conf.interpolations

        ret = configurable.conf.resolve(inplace=True)
        assert ret is None
        assert len(configurable.conf.interpolations) == 0
        cont = OmegaConf.to_container(configurable.config, resolve=False)
        interps_keys = [
            k for k in cont.keys() if OmegaConf.is_interpolation(configurable.config, k)
        ]
        assert len(interps_keys) == 0
        if len(interps):
            for k in cont.keys():
                assert not OmegaConf.is_interpolation(configurable.config, k)

    def test_resolve_inplace_key(self, configurable):
        ret = configurable.conf.resolve(key="integer", inplace=True)
        assert ret is None
        assert len(configurable.conf.interpolations) == 0
        cont = OmegaConf.to_container(configurable.config, resolve=False)
        interps = {
            k: v
            for k, v in cont.items()
            if OmegaConf.is_interpolation(configurable.config, str(k))
        }
        assert len(interps) == 0

    def test_resolve_not_inplace_not_key(self, configurable):
        interps = configurable.conf.interpolations
        ret = configurable.conf.resolve(inplace=False)
        assert isinstance(ret, dict)
        assert all([hasattr(configurable, k) for k in ret.keys()])
        assert len(configurable.conf.interpolations) == len(interps)
        cont = OmegaConf.to_container(configurable.config, resolve=False)
        interps_keys = [
            k for k in cont.keys() if OmegaConf.is_interpolation(configurable.config, k)
        ]
        assert len(interps_keys) == len(interps)

    def test_resolve_not_inplace_key(self, configurable):
        interps = configurable.conf.interpolations
        ret = configurable.conf.resolve(key="integer", inplace=False)
        assert not isinstance(ret, str)
        assert not isinstance(ret, float)
        assert hasattr(configurable, "integer")
        assert isinstance(configurable.integer, int)
        assert len(configurable.conf.interpolations) == len(interps)
        cont = OmegaConf.to_container(configurable.config, resolve=False)
        interps_keys = [
            k for k in cont.keys() if OmegaConf.is_interpolation(configurable.config, k)
        ]
        assert len(interps_keys) == len(interps)

    def test_to_param_type(self, configurable):
        interp_0 = configurable.conf.interpolations
        for k in configurable.config.keys():
            param_val = getattr(configurable, k)
            to_ptype_self = configurable.conf.to_param_type(k)
            assert param_val == to_ptype_self, (
                f"key: {k}, conf: {configurable.config} interps {configurable.conf.interpolations}"
                f" number {configurable.number}"
            )

            if configurable.conf.is_interpolation(k):
                unresolved = OmegaConf.to_container(configurable.config, resolve=False)
                interp_1 = configurable.conf.interpolations
                assert interp_1 == interp_0
                assert len(interp_1) > 0
                assert k in interp_0
                assert k in interp_1
                assert interp_1[k] != param_val
                assert interp_1[k] != param_val
                assert isinstance(unresolved[k], str)
                if not isinstance(configurable.conf.params[k], param.String):
                    assert not isinstance(param_val, str)

    def __test_update_value(self, configurable):
        c = configurable.conf
        if "integer" in c.config:
            configurable.integer = 777
            configurable.config.integer = 777
            configurable.number = 42.0
            configurable.config.number = 42.0
            c.update_value("integer", "${number}")
            assert configurable.integer == int(configurable.number)
            assert isinstance(configurable.integer, int) and isinstance(configurable.number, float)
            assert "integer" in c.interpolations

    def test_sync(self, interpolated):
        interps = interpolated.conf.interpolations
        assert len(interps) > 0, f"conf {interpolated.config} interps: {interps}"
        interpolated.conf.sync()
        for k in interps:
            assert interpolation_is_consistent(interpolated, k)
        assert len(interpolated.conf.interpolations) > 0


class TestConfigurable:
    def test_conf(self, configurable):
        assert hasattr(configurable, "conf")
        assert hasattr(configurable, "_Configurable__conf")
        assert configurable.conf == configurable._Configurable__conf
        assert isinstance(configurable.conf, Config)
        with pytest.raises(AttributeError):
            configurable.conf = "fails"

    def test_config(self, configurable):
        assert isinstance(configurable.config, omegaconf.DictConfig)
        assert isinstance(configurable.param.config, DictConfig)
        assert not configurable.param.config.readonly
        assert configurable.param.config.per_instance
        assert configurable.param.config.instantiate
