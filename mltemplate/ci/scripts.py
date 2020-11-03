from mltemplate.ci.commands import (
    bump_version_install,
    bump_version_script,
    coverage_script,
    install_python_project,
    is_bump_version_commit,
    is_tag_commit,
    pypi_deploy_script,
    pypi_install,
    pypi_script,
    style_install,
    style_script,
)
from mltemplate.ci.core import Command, Phase


class InstallProject(Command):
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


class RunPytest(Command):
    def __init__(self, name="coverage", as_string: bool = False, aliased: bool = True):
        super(RunPytest, self).__init__(
            name=name, cmd=coverage_script, as_string=as_string, aliased=aliased
        )


class BumpVersionInstall(Command):
    def __init__(
        self, name="install_bump_version", as_string: bool = False, aliased: bool = False
    ):
        super(BumpVersionInstall, self).__init__(
            name=name, cmd=bump_version_install, as_string=as_string, aliased=aliased
        )


class RunBumpVersion(Command):
    def __init__(self, name="run_bump_version", as_string: bool = False, aliased: bool = False):
        super(RunBumpVersion, self).__init__(
            name=name, cmd=bump_version_script, as_string=as_string, aliased=aliased
        )


class PypiInstall(Command):
    def __init__(self, name="install_pypi", as_string: bool = False, aliased: bool = False):
        super(PypiInstall, self).__init__(
            name=name, cmd=pypi_install, as_string=as_string, aliased=aliased
        )


class PypiBuild(Command):
    def __init__(self, name="pypi_build", as_string: bool = False, aliased: bool = False):
        super(PypiBuild, self).__init__(
            name=name, cmd=pypi_script, as_string=as_string, aliased=aliased
        )


class PypiDeployCmd(Command):
    def __init__(self, name="pypi_deploy", as_string: bool = False, aliased: bool = False):
        super(PypiDeployCmd, self).__init__(
            name=name, cmd=pypi_deploy_script, as_string=as_string, aliased=aliased
        )


class PypiDeploy(Phase):
    def __init__(self, name="pypi_deploy"):
        super(PypiDeploy, self).__init__(
            name=name,
            provider="script",
            script=PypiDeployCmd(),
            skip_cleanup=True,
            on={"tags": True},
        )


class StyleCheckInstall(Command):
    def __init__(self, name="style_install", as_string: bool = False, aliased: bool = False):
        super(StyleCheckInstall, self).__init__(
            name=name, cmd=style_install, as_string=as_string, aliased=aliased
        )


class StyleCheckRun(Command):
    def __init__(self, name="style_run", as_string: bool = False, aliased: bool = False):
        super(StyleCheckRun, self).__init__(
            name=name, cmd=style_script, as_string=as_string, aliased=aliased
        )


class NoBumpVersionCommit(Command):
    def __init__(
        self, name="no_version_bump_commit", as_string: bool = False, aliased: bool = True
    ):
        super(NoBumpVersionCommit, self).__init__(
            name=name,
            cmd=["commit_message !~ /^Bump version/"],
            as_string=as_string,
            aliased=aliased,
        )


class IsBumpVersionCommit(Command):
    def __init__(
        self, name="is_version_bump_commit", as_string: bool = False, aliased: bool = True
    ):
        super(IsBumpVersionCommit, self).__init__(
            name=name, cmd=is_bump_version_commit, as_string=as_string, aliased=aliased,
        )


class IsTagCommit(Command):
    def __init__(self, name="is_tag_commit", as_string: bool = False, aliased: bool = True):
        super(IsTagCommit, self).__init__(
            name=name, cmd=is_tag_commit, as_string=as_string, aliased=aliased,
        )
