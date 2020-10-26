import pytest

from mltemplate.ci.scripts import InstallProject


@pytest.fixture()
def script():
    return InstallProject()


class TestScript:
    def test_init(self, script):
        pass

    def test_print(self, script):
        pass

    def test_compile(self, script):
        script.compile()
