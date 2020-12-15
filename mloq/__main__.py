"""Command line interface for mloq."""
import os
from pathlib import Path
import sys

from mloq.api import init_repository


def main():
    """Initialize the target repo."""
    root_path = Path(os.getcwd())
    init_repository(root_path, override=False)


if __name__ == "__main__":
    sys.exit(main())
