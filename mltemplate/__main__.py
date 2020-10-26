import os
from pathlib import Path
import sys

import yaml
from yaml import Loader

from mltemplate.directories import setup_project


def main():
    """Initialize the target repo."""
    root_path = Path(os.getcwd())
    with open(root_path / "repository.yaml", "r") as config:
        params_d = yaml.load(config.read(), Loader)
    print(params_d)
    setup_project(params_d, root_path)


if __name__ == "__main__":
    sys.exit(main())
