from pathlib import Path
import tempfile

import pytest

from mloq.files import File
from mloq.requirements import (
    compose_requirements,
    get_aliased_requirements_file,
    read_requirements_file,
    write_dev_requirements,
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


def test_reqd_requirements_file(option):
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


def test_write_dev_requirements():
    with tempfile.TemporaryDirectory() as tmp:
        write_dev_requirements(tmp)
