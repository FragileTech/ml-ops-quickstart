import pytest

from mltemplate.ci.jobs import RunTests, StyleCheck


@pytest.fixture()
def job():
    return RunTests()


def test_job(job):
    job.compile()


def test_dict(job):
    job.compile()
    # for script in job().values():
    #    print(str(script.compile()))
