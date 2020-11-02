import pytest

from mltemplate.ci.jobs import RunTestsJob, StyleCheckJob


@pytest.fixture()
def job():
    return RunTestsJob()


def test_job(job):
    job.compile()


def test_dict(job):
    job.compile()
    # for script in job().values():
    #    print(str(script.compile()))
