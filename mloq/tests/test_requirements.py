from pathlib import Path
import tempfile

import pytest

from mloq.files import File, test_req
from mloq.requirements import (
    compose_requirements,
    get_aliased_requirements_file,
    install_requirement_file,
    install_requirements,
    read_requirements_file,
    require_cuda,
    write_dev_requirements,
    write_project_requirements,
)


all_options = [
    "data-science",
    "datascience",
    "ds",
    "pytorch",
    "torch",
    "tensorflow",
    "tf",
    "data-visualization",
    "data-viz",
    "data-vis",
    "dataviz",
    "datavis",
]

requirements_all = ("data-science", "torch", "tf", "dataviz")


@pytest.fixture(params=all_options)
def option(request):
    return request.param


@pytest.fixture()
def all_requirements():
    return requirements_all


def test_get_aliased_requirements_file(option):
    val = get_aliased_requirements_file(option)
    assert isinstance(val, File)
    with pytest.raises(KeyError):
        get_aliased_requirements_file("miau")


def test_read_requirements_file(option):
    text = read_requirements_file(option)
    assert isinstance(text, str)


def test_compose_requirements(all_requirements):
    file = compose_requirements(all_requirements)
    lines = file.split("\n")
    test_file_path = Path(__file__).parent / "dummy_reqs.txt"
    with open(test_file_path, "r") as f:
        example_lines = f.read().split("\n")
    for line, example in zip(lines, example_lines):
        lib_name = line.split("==")[0]
        assert lib_name == example


def test_write_dev_requirements(ledger):
    with tempfile.TemporaryDirectory() as tmp:
        write_dev_requirements(ledger, tmp)
        write_dev_requirements(ledger, tmp, False, False, False)


def test_require_cuda():
    assert not require_cuda()
    assert not require_cuda(project_config={"requirements": "none"})
    assert not require_cuda(project_config={"requirements": "datascience"})
    assert require_cuda(project_config={"requirements": "torch"})


def test_write_project_requirements(ledger):
    assert write_project_requirements(["None"], ledger) is None


def test_install_requirements_file():
    result = install_requirement_file(test_req.src)
    assert result.ok


def test_install_requirements():
    install_requirements(".", test_req.src, test_req.src, test_req.src)
