import os
from pathlib import Path
import sys

from mltemplate.directories import setup_project_project_files
from mltemplate.parse_config import parse_config
from mltemplate.requirements import setup_requirements


def main():
    """Initialize the target repo."""
    root_path = Path(os.getcwd())
    params_d = parse_config(root_path / "repository.yaml")
    if "template" in params_d:
        print("creating files with template %s" % params_d["template"])
        setup_project_project_files(params_d["template"], root_path)
    if "requirements" in params_d:
        print("creating requirements with template %s" % params_d["template"])
        setup_requirements(params_d["requirements"], root_path)


if __name__ == "__main__":
    sys.exit(main())
