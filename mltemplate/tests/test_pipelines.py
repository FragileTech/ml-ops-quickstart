import pytest

from mltemplate.ci.core import Pipeline
from mltemplate.ci.stages import PytestStage, StyleCheckStage
from mltemplate.ci.writers import swap_dictionary_key, yaml_as_string


@pytest.fixture(params=[[StyleCheckStage()], [PytestStage()], [StyleCheckStage(), PytestStage()]])
def pipeline(request):
    return Pipeline(name="miau", stages=request.param)


def test_travis(pipeline):
    pipeline.compile_aliases()
    pipeline.compile_stages()
