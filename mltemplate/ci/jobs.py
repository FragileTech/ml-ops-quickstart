from mltemplate.ci.core import Job, PythonJob
from mltemplate.ci.scripts import (
    BumpVersionInstall,
    InstallProject,
    IsBumpVersionCommit,
    NoBumpVersionCommit,
    RunBumpVersion,
    RunPytest,
    StyleCheckInstall,
    StyleCheckRun,
)


class StyleCheckJob(PythonJob):
    def __init__(
        self,
        name="check_code_style",
        stage=None,
        python_version=3.8,
        install=StyleCheckInstall(),
        script=StyleCheckRun(),
        condition=NoBumpVersionCommit(),
    ):
        super(StyleCheckJob, self).__init__(
            name=name,
            python_version=python_version,
            stage=stage,
            install=install,
            script=script,
            condition=condition,
        )


class RunTestsJob(PythonJob):
    def __init__(
        self,
        name="run_tests",
        stage="test",
        python_version=3.6,
        install=InstallProject(),
        script=RunPytest(),
        condition=NoBumpVersionCommit(),
    ):
        name = f"{name}_py{str(python_version).replace('.', '')}"
        super(RunTestsJob, self).__init__(
            name=name,
            python_version=python_version,
            stage=stage,
            install=install,
            script=script,
            condition=condition,
        )


class BumpVersionJob(Job):
    def __init__(
        self,
        name="bump_version",
        stage="bump-version",
        python_version=3.6,
        install=BumpVersionInstall(),
        script=RunBumpVersion(),
        condition=IsBumpVersionCommit(),
    ):
        super(BumpVersionJob, self).__init__(
            name=name,
            python_version=python_version,
            stage=stage,
            install=install,
            script=script,
            condition=condition,
        )
