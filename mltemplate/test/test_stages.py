import pytest

from mltemplate.ci.stages import StyleCheckStage, Pytest


@pytest.fixture()
def stage():
    return Pytest()  # StyleCheckStage()


def test_style_test(stage):
    stage.compile()
