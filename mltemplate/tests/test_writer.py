from pathlib import Path

import pytest

from mltemplate.ci.writers import GitLab, Travis
from mltemplate.tests.test_pipelines import pipeline


def test_travis(pipeline):
    travis = Travis(pipeline)
    travis.dump(Path(__file__).parent / ".travis.yml")
    # print(travis)


def test_gitlab(pipeline):
    gitlab = GitLab(pipeline)
    print(gitlab)
