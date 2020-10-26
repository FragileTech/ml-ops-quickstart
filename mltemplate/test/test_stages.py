import pytest

from mltemplate.ci.stages import Pytest, StyleCheckStage


@pytest.fixture(params=[StyleCheckStage, Pytest])
def stage(request):
    return request.param()


def test_style_test(stage):
    stage.compile()
