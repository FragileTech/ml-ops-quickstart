import copy
import os

from mloq.config.setup_generation import (
    _generate_project_config,
    _generate_template_config,
    generate_config,
)


def compare_dicts(a, b):
    for (k1, v1), (k2, v2) in zip(sorted(a.items()), sorted(b.items())):
        assert k1 == k2
        if not isinstance(v1, list):
            assert v1 == v2, k1
        else:
            for x1, x2 in zip(v1, v2):
                assert x1 == x2, k1


def test_generate_project_config(config):
    _config = copy.deepcopy(config)
    _config.project.requirements = None
    os.environ["MLOQ_REQUIREMENTS"] = "torch"
    try:
        new_project = _generate_project_config(_config)
        compare_dicts(config.project, new_project)
    finally:
        del os.environ["MLOQ_REQUIREMENTS"]


def test_generate_template_config(config):
    _config = copy.deepcopy(config)
    _config.template.project_name = None
    os.environ["MLOQ_PROJECT_NAME"] = "test_project"
    try:
        new_template = _generate_template_config(_config)
        compare_dicts(config.template, new_template)
    finally:
        del os.environ["MLOQ_PROJECT_NAME"]


def test_generate_config(config):
    _config = copy.deepcopy(config)
    _config.project.requirements = None
    _config.template.project_name = None
    os.environ["MLOQ_REQUIREMENTS"] = "torch"
    os.environ["MLOQ_PROJECT_NAME"] = "test_project"
    try:
        new_config = generate_config(_config)
        compare_dicts(config, new_config)
    finally:
        del os.environ["MLOQ_REQUIREMENTS"]
        del os.environ["MLOQ_PROJECT_NAME"]
