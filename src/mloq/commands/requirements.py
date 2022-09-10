"""Mloq requirements command implementation."""
from pathlib import Path
import tempfile
from typing import Iterable, List, Union

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.config.param_patch import param
from mloq.files import ASSETS_PATH, File, file
from mloq.record import CMDRecord


# Requirements files
REQUIREMENTS_PATH = ASSETS_PATH / "requirements"
requirements = file(
    "requirements.txt",
    REQUIREMENTS_PATH,
    "list of exact versions of the packages on which your project depends",
    is_static=True,
)
data_science_req = file(
    "data-science.txt",
    REQUIREMENTS_PATH,
    "list of commonly used data science libraries",
)
data_viz_req = file(
    "data-visualization.txt",
    REQUIREMENTS_PATH,
    "list of commonly used visualization libraries",
    is_static=True,
)
pytorch_req = file(
    "pytorch.txt",
    REQUIREMENTS_PATH,
    "Pytorch deep learning libraries",
    is_static=True,
)
tensorflow_req = file(
    "tensorflow.txt",
    REQUIREMENTS_PATH,
    "Tensorflow deep learning libraries",
    is_static=True,
)
lint_req = file(
    "requirements-lint.txt",
    REQUIREMENTS_PATH,
    "list of exact versions of the packages used to check your code style",
    is_static=True,
)
test_req = file(
    "requirements-test.txt",
    REQUIREMENTS_PATH,
    "list of exact versions of the packages needed to run your test suite",
    is_static=True,
)
dogfood_req = file(
    "dogfood.txt",
    REQUIREMENTS_PATH,
    "list of mock requirements for testing purposes",
    is_static=True,
)
docs_req = file(
    "requirements-docs.txt",
    REQUIREMENTS_PATH,
    "list of exact versions of the packages needed to build your documentation",
    is_static=True,
)
REQUIREMENTS_FILES = [pytorch_req, data_science_req, data_viz_req, tensorflow_req]

REQUIREMENT_CHOICES = [
    "data-science",
    "data-viz",
    "torch",
    "tensorflow",
    "none",
    "dogfood",
    "None",
]


class RequirementsCMD(Command):
    """Implement the functionality of the requirements Command."""

    cmd_name = "requirements"
    files = tuple(REQUIREMENTS_FILES)
    disable = param.Boolean(default=None, doc="Disable requirements command?")
    requirements = param.ListSelector(
        default=["none"],
        doc="Project requirements",
        objects=REQUIREMENT_CHOICES,
    )
    REQUIREMENTS_ALIASES = {
        data_science_req: ["data-science", "datascience", "ds"],
        pytorch_req: ["pytorch", "torch"],
        tensorflow_req: ["tensorflow", "tf"],
        data_viz_req: ["data-visualization", "data-viz", "data-vis", "dataviz", "datavis"],
    }

    def __init__(self, record: CMDRecord, interactive: bool = False):
        """
        Initialize a RequirementsCMD class.

        Args:
            record: CMDRecord where the command data will be written.
            interactive: If True, parse the command configuration in interactive mode.
        """
        super(RequirementsCMD, self).__init__(record=record, interactive=interactive)
        self._temp_dir = tempfile.TemporaryDirectory()
        # File objects work referencing files present in the system. We create a requirements.txt
        # temporary file to be consistent with that behavior.
        reqs_src = Path(self._temp_dir.name) / "requirements.txt"
        self._reqs_file = File(
            name=requirements.name,
            src=reqs_src,
            dst=requirements.dst,
            is_static=requirements.is_static,
            description=requirements.description,
        )
        self.files = tuple(list(self.files) + [self._reqs_file])

    def __del__(self) -> None:
        """Remove the temporary directory when the instance is deleted."""
        self._temp_dir.cleanup()

    @classmethod
    def get_aliased_requirements_file(cls, option: str) -> File:
        """Get requirement file from aliased name."""
        for _file, valid_alias in cls.REQUIREMENTS_ALIASES.items():
            if option in valid_alias:
                return _file
        if option == "dogfood":
            return dogfood_req
        raise KeyError(
            f"{option} is not a valid name. Valid aliases are {cls.REQUIREMENTS_ALIASES}",
        )

    @classmethod
    def read_requirements_file(cls, option: str) -> str:
        """Return the content of the target requirements file form an aliased name."""
        req_file = cls.get_aliased_requirements_file(option)
        with open(req_file.src, "r") as f:
            return f.read()

    @classmethod
    def compose_requirements(cls, options: Iterable[str]) -> str:
        """
        Return the content requirements.txt file with pinned dependencies.

        The returned string contains the combined dependencies\
         for the different options sorted alphabetically.

        Args:
            options: Iterable containing the aliased names of the target \
                     dependencies for the project.

        Returns:
            str containing the pinned versions of all the selected requirements.
        """
        requirements_text = ""
        for i, opt in enumerate(options):
            pref = "\n" if i > 0 else ""  # Ensure one requirement per line
            requirements_text += pref + cls.read_requirements_file(opt)
        # Sort requirements alphabetically
        requirements_text = "\n".join(sorted(requirements_text.split("\n"))).lstrip("\n")
        return requirements_text

    '''def ___parse_config(self) -> DictConfig:
        """Update the configuration DictConfig with the Command parameters."""
        value = self.CONFIG.requirements(self.record.config, self.interactive)
        self.record.config.requirements = value
        return self.record.config'''

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Please specify the requirements of the project as a comma separated list.")
        click.echo("Available values:")
        click.echo(
            "    data-science: Common data science libraries such as numpy, pandas, sklearn...",
        )
        click.echo(
            (
                "    data-viz: Visualization libraries such as holoviews, ",
                "bokeh, plotly, matplotlib...",
            ),
        )
        click.echo("    pytorch: Latest version of pytorch, torchvision and pytorch_lightning")
        click.echo("    tensorflow: ")  # , data-viz, torch, tensorflow}")
        return self.parse_config()

    @staticmethod
    def requirements_is_empty(options: Union[List[str], str]) -> bool:
        """Return True if no requirements are specified for the project."""
        if not options:
            return True
        if isinstance(options, str):
            options = [options]
        if None in options or "None" in options or "none" in options:
            return True
        return False

    def record_files(self) -> None:
        """Register the files that will be generated by mloq."""
        reqs_value = self.record.config.requirements.requirements
        if self.requirements_is_empty(reqs_value):
            return
        reqs_content = self.compose_requirements(reqs_value)
        with open(self._reqs_file.src, "w") as f:
            f.write(reqs_content)

        self.record.register_file(file=self._reqs_file, path=Path())
