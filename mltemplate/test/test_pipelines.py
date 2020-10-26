import pytest
from mltemplate.ci.pipelines import Pipeline
from mltemplate.ci.stages import StyleCheckStage, Pytest
from mltemplate.ci.writers import swap_dictionary_key, yaml_as_string


@pytest.fixture(params=[[StyleCheckStage(), Pytest()], [Pytest()], [StyleCheckStage()]])
def pipeline(request):
    return Pipeline(name="miau", stages=request.param)


def test_travis(pipeline):
    pipeline.compile_aliases()
    pipeline.compile_stages()
    # print(pipeline.compile_stages(True))
    # for job in pipeline.stages:
    #    print("STAGES", type(job), type(pipeline.stages))
