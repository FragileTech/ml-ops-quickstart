"""Command line interface for mloq."""
import sys

from mloq.cli import cli


if __name__ == "__main__":
    sys.exit(cli(auto_envvar_prefix="MLOQ"))
