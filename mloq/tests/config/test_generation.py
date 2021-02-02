import copy
import os

from mloq.config.generation import generate_project_config, generate_template


def compare_dicts(a, b):
    for (k1, v1), (k2, v2) in zip(a.items(), b.items()):
        assert k1 == k2
        if not isinstance(v1, list):
            assert v1 == v2
        else:
            for x1, x2 in zip(v1, v2):
                assert x1 == x2


def test_generate_config(project_config):
    in_config = copy.deepcopy(project_config)
    in_config["requirements"] = None
    os.environ["MLOQ_REQUIREMENTS"] = "torch"
    new_template = generate_project_config(project_config=in_config, interactive=False)
    del os.environ["MLOQ_REQUIREMENTS"]
    compare_dicts(project_config, new_template)


def test_generate_template(template, project_config):
    in_template = copy.deepcopy(template)
    in_template["project_name"] = None
    os.environ["MLOQ_PROJECT_NAME"] = "test_project"
    new_template = generate_template(
        template=in_template,
        project_config=project_config,
        interactive=False,
    )
    del os.environ["MLOQ_PROJECT_NAME"]
    compare_dicts(template, new_template)
