from mltemplate.ci.commands import (
    install_python_project,
    coverage_script,
    style_script,
    style_install,
    docker_test_script,
    dockerhub_install,
    dockerhub_script,
    dockerhub_deploy_script,
    bump_version_script,
    bump_version_install,
    pypi_install,
    pypi_deploy_script,
    pypi_script,
)

from mltemplate.ci.core import Script


class InstallProject(Script):
    def __init__(
        self, name="install", as_string: bool = False, aliased: bool = True, no_format=True
    ):
        super(InstallProject, self).__init__(
            name=name,
            cmd=install_python_project,
            as_string=as_string,
            aliased=aliased,
            no_format=no_format,
        )


class RunPytest(Script):
    def __init__(self, name="run_pytest", as_string: bool = False, aliased: bool = True):
        super(RunPytest, self).__init__(
            name=name, cmd=coverage_script, as_string=as_string, aliased=aliased
        )


class BumpVersionInstall(Script):
    def __init__(
        self, name="install_bump_version", as_string: bool = False, aliased: bool = False
    ):
        super(BumpVersionInstall, self).__init__(
            name=name, cmd=bump_version_install, as_string=as_string, aliased=aliased
        )


class RunBumpVersion(Script):
    def __init__(self, name="run_bump_version", as_string: bool = False, aliased: bool = False):
        super(RunBumpVersion, self).__init__(
            name=name, cmd=bump_version_script, as_string=as_string, aliased=aliased
        )


class PypiInstall(Script):
    def __init__(self, name="install_pypi", as_string: bool = False, aliased: bool = False):
        super(PypiInstall, self).__init__(
            name=name, cmd=pypi_install, as_string=as_string, aliased=aliased
        )


class PypiBuild(Script):
    def __init__(self, name="pypi_build", as_string: bool = False, aliased: bool = False):
        super(PypiBuild, self).__init__(
            name=name, cmd=pypi_script, as_string=as_string, aliased=aliased
        )


class PypiDeploy(Script):
    def __init__(self, name="pypi_deploy", as_string: bool = False, aliased: bool = False):
        super(PypiDeploy, self).__init__(
            name=name, cmd=pypi_deploy_script, as_string=as_string, aliased=aliased
        )


class StyleCheckInstall(Script):
    def __init__(self, name="style_install", as_string: bool = False, aliased: bool = False):
        super(StyleCheckInstall, self).__init__(
            name=name, cmd=style_install, as_string=as_string, aliased=aliased
        )


class StyleCheckRun(Script):
    def __init__(self, name="style_run", as_string: bool = False, aliased: bool = False):
        super(StyleCheckRun, self).__init__(
            name=name, cmd=style_script, as_string=as_string, aliased=aliased
        )


class NoBumpVersionCommit(Script):
    def __init__(
        self, name="no_version_bump_commit", as_string: bool = True, aliased: bool = True
    ):
        super(NoBumpVersionCommit, self).__init__(
            name=name,
            cmd=["commit_message !~ /^Bump version/"],
            as_string=as_string,
            aliased=aliased,
        )
