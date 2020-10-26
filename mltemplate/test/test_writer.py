import pytest

from mltemplate.ci.writers import Travis, GitLab
from mltemplate.test.test_pipelines import pipeline


def test_travis(pipeline):
    travis = Travis(pipeline)
    travis.compile()
    # print(travis)


def test_gitlab(pipeline):
    gitlab = GitLab(pipeline)
    print(gitlab)
