from mltemplate.ci.core import PythonJob
from mltemplate.ci.scripts import (
    InstallProject,
    NoBumpVersionCommit,
    RunPytest,
    StyleCheckInstall,
    StyleCheckRun,
)


class StyleCheck(PythonJob):
    def __init__(
        self,
        name="check_code_style",
        stage=None,
        python_version=3.6,
        install=StyleCheckInstall(),
        script=StyleCheckRun(),
        condition=NoBumpVersionCommit(),
    ):
        super(StyleCheck, self).__init__(
            name=name,
            python_version=python_version,
            stage=stage,
            install=install,
            script=script,
            condition=condition,
        )


class RunTests(PythonJob):
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
        super(RunTests, self).__init__(
            name=name,
            python_version=python_version,
            stage=stage,
            install=install,
            script=script,
            condition=condition,
        )
