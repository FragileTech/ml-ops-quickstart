from mltemplate.ci.core import Stage
from mltemplate.ci.jobs import BumpVersionJob, RunTestsJob, StyleCheckJob


class BumpVersionStage(Stage):
    def __init__(self, name="bump-version", **kwargs):
        super(BumpVersionStage, self).__init__(
            name=name, jobs=[BumpVersionJob(stage=name, **kwargs)]
        )
        self.set_job_stages(name)


class StyleCheckStage(Stage):
    def __init__(self, name="style", **kwargs):
        super(StyleCheckStage, self).__init__(
            name=name, jobs=[StyleCheckJob(stage=name, **kwargs)]
        )
        self.set_job_stages(name)


class Pytest(Stage):
    def __init__(self, name="test", python_versions=None, **kwargs):
        self.python_versions = [3.6, 3.7, 3.8] if python_versions is None else python_versions
        jobs = self._init_jobs(stage=name, **kwargs)
        super(Pytest, self).__init__(name=name, jobs=jobs)

    def _init_jobs(self, stage, **kwargs):
        def init_test(v, codecov):
            job = RunTestsJob(python_version=v, stage=stage, **kwargs)
            if codecov:
                job["after_success"] = ["codecov"]
            return job

        last_item = len(self.python_versions) - 1
        return [init_test(v, i == last_item) for i, v in enumerate(self.python_versions)]
