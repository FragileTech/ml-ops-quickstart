import pytest

from mltemplate.ci.stages import PytestStage, StyleCheckStage


@pytest.fixture(params=[StyleCheckStage, PytestStage])
def stage(request):
    return request.param()


def test_style_test(stage):
    stage.compile()
