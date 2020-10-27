import os
from pathlib import Path

from mltemplate.directories import REQUIREMENTS_PATH, _copy_file


def get_requirements_filename(option):
    aliases = {"data-science.txt": ["data-science", "datascience", "ds"],
               "pytorch.txt": ["pytorch", "torch"],
               "data-visualization.txt": ["data-visualization", "data-viz", "data-vis", "dataviz", "datavis"],
               }
    for filename, valid_alias in aliases.items():
        if option in valid_alias:
            return filename
    raise KeyError(f"{option} is not a valid name. Valid aliases are {aliases}")


def get_requirements_file(option, requirements_path=REQUIREMENTS_PATH):
    file_name = get_requirements_filename(option)
    with open(requirements_path / file_name, "r") as f:
        return f.read()


def compose_requirements(options):
    requirements_text = ""
    for i, opt in enumerate(options):
        pref = "\n" if i > 0 else ""
        requirements_text += pref + get_requirements_file(opt)
    return requirements_text


def write_requirements(options, out_path=None, out_name="requirements.txt"):
    out_path = os.getcwd() if out_path is None else out_path
    requirements = compose_requirements(options) if options is not None else ""
    with open(out_path / out_name, "w") as f:
        f.write(requirements)


def write_dev_requirements(out_path):
    out_path = os.getcwd() if out_path is None else out_path
    _copy_file(REQUIREMENTS_PATH / "requirements-lint.txt", out_path / "requirements-lint.txt")
    _copy_file(REQUIREMENTS_PATH / "requirements-dev.txt", out_path / "requirements-dev.txt")


def setup_requirements(options, out_path=None, out_name="requirements.txt"):
    out_path = os.getcwd() if out_path is None else out_path
    write_requirements(options=options, out_path=out_path, out_name=out_name)
    write_dev_requirements(out_path)
