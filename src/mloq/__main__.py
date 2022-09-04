"""Command line interface for mloq."""
import sys

from mloq.cli import cli


# from mloq.commands.globals import globals


if __name__ == "__main__":
    sys.exit(cli())
